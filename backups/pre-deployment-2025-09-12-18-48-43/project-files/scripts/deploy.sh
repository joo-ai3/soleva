#!/bin/bash

# Soleva Docker Deployment Script
# This script handles the complete deployment of the Soleva platform using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="soleva"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check if .env file exists
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "docker.env.example" ]; then
            warn ".env file not found. Copying from docker.env.example..."
            cp docker.env.example .env
            warn "Please edit .env file with your actual configuration before proceeding."
            exit 1
        else
            error ".env file not found and docker.env.example doesn't exist."
        fi
    fi
    
    log "✅ Prerequisites check passed"
}

generate_ssl_dhparam() {
    log "Generating SSL DH parameters..."
    
    if [ ! -f "nginx/ssl/dhparam.pem" ]; then
        mkdir -p nginx/ssl
        openssl dhparam -out nginx/ssl/dhparam.pem 2048
        log "✅ DH parameters generated"
    else
        log "✅ DH parameters already exist"
    fi
}

setup_ssl_certificates() {
    log "Setting up SSL certificates..."
    
    # Load environment variables
    source .env
    
    # Create directories
    mkdir -p nginx/ssl
    
    # Check if certificates already exist
    if [ -d "/etc/letsencrypt/live/${DOMAIN}" ] || [ -d "letsencrypt/live/${DOMAIN}" ]; then
        log "✅ SSL certificates already exist"
        return
    fi
    
    info "Obtaining SSL certificates for ${DOMAIN}..."
    
    # Start nginx temporarily for certificate validation
    docker-compose up -d nginx
    sleep 10
    
    # Obtain certificates
    docker-compose run --rm certbot || {
        warn "Failed to obtain SSL certificate automatically."
        warn "You may need to manually configure SSL certificates."
    }
    
    log "✅ SSL certificate setup completed"
}

build_and_deploy() {
    log "Building and deploying Soleva platform..."
    
    # Pull latest images
    docker-compose pull
    
    # Build custom images
    docker-compose build --no-cache
    
    # Start all services
    docker-compose up -d
    
    log "✅ Deployment completed"
}

wait_for_services() {
    log "Waiting for services to be ready..."
    
    # Wait for database
    docker-compose exec postgres pg_isready -U ${DB_USER} -d ${DB_NAME} || {
        info "Waiting for PostgreSQL to be ready..."
        sleep 30
    }
    
    # Wait for backend
    timeout 300 bash -c 'until curl -f http://localhost/api/health/ &>/dev/null; do sleep 5; done' || {
        warn "Backend health check failed. Please check the logs."
    }
    
    log "✅ Services are ready"
}

run_migrations() {
    log "Running database migrations..."
    
    # Backend migrations are handled by the entrypoint script
    # But we can verify they ran successfully
    docker-compose exec backend python manage.py showmigrations --plan | grep -q "\[X\]" || {
        warn "Some migrations may not have run. Check backend logs."
    }
    
    log "✅ Database migrations completed"
}

show_status() {
    echo ""
    echo "📊 Deployment Status"
    echo "===================="
    
    # Service status
    docker-compose ps
    
    echo ""
    echo "🔗 Service URLs:"
    echo "Frontend: https://solevaeg.com"
    echo "Backend API: https://solevaeg.com/api"
    echo "Admin Panel: https://solevaeg.com/admin"
    
    echo ""
    echo "📋 Quick Commands:"
    echo "View logs: docker-compose logs -f [service_name]"
    echo "Restart service: docker-compose restart [service_name]"
    echo "Stop all: docker-compose down"
    echo "Update: ./scripts/deploy.sh update"
    
    log "🎉 Deployment completed successfully!"
}

backup_data() {
    log "Creating backup..."
    
    # Create backup directory
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    docker-compose exec postgres pg_dump -U ${DB_USER} ${DB_NAME} | gzip > "$BACKUP_DIR/database.sql.gz"
    
    # Backup media files
    docker cp soleva_backend:/app/media "$BACKUP_DIR/"
    
    log "✅ Backup created in $BACKUP_DIR"
}

update_deployment() {
    log "Updating deployment..."
    
    # Create backup first
    backup_data
    
    # Pull latest code (assumes git repository)
    if [ -d ".git" ]; then
        git pull origin main
    fi
    
    # Rebuild and restart services
    docker-compose build --no-cache
    docker-compose up -d
    
    log "✅ Update completed"
}

cleanup() {
    log "Cleaning up unused Docker resources..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes (be careful with this)
    # docker volume prune -f
    
    # Remove unused networks
    docker network prune -f
    
    log "✅ Cleanup completed"
}

# Main execution
case "${1:-deploy}" in
    "deploy")
        check_prerequisites
        generate_ssl_dhparam
        setup_ssl_certificates
        build_and_deploy
        wait_for_services
        run_migrations
        show_status
        ;;
    "update")
        update_deployment
        ;;
    "backup")
        backup_data
        ;;
    "ssl")
        setup_ssl_certificates
        ;;
    "status")
        show_status
        ;;
    "cleanup")
        cleanup
        ;;
    "logs")
        docker-compose logs -f ${2:-}
        ;;
    "restart")
        docker-compose restart ${2:-}
        ;;
    "stop")
        docker-compose down
        ;;
    "help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  deploy    - Full deployment (default)"
        echo "  update    - Update deployment with latest code"
        echo "  backup    - Create backup of database and media"
        echo "  ssl       - Setup SSL certificates"
        echo "  status    - Show deployment status"
        echo "  cleanup   - Clean up unused Docker resources"
        echo "  logs      - Show logs (optionally specify service)"
        echo "  restart   - Restart services (optionally specify service)"
        echo "  stop      - Stop all services"
        echo "  help      - Show this help"
        ;;
    *)
        error "Unknown command: $1. Use '$0 help' for usage information."
        ;;
esac
