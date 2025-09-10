#!/bin/bash

# Soleva Production Deployment Script
# This script automates the deployment process for the Soleva e-commerce platform

set -e  # Exit on any error

echo "🚀 Starting Soleva Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/var/www/soleva-platform"
BACKEND_DIR="$PROJECT_DIR/soleva back end"
FRONTEND_DIR="$PROJECT_DIR/soleva front end"
BACKUP_DIR="/var/backups/soleva"
LOG_FILE="/var/log/soleva-deploy.log"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if running as root or with sudo
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root or with sudo"
    fi
    
    # Check if required commands exist
    commands=("git" "npm" "python3" "pip" "nginx" "systemctl" "postgresql")
    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            error "Required command '$cmd' not found"
        fi
    done
    
    # Check if project directory exists
    if [[ ! -d "$PROJECT_DIR" ]]; then
        error "Project directory $PROJECT_DIR not found"
    fi
    
    log "✅ Prerequisites check passed"
}

backup_database() {
    log "Creating database backup..."
    
    mkdir -p "$BACKUP_DIR"
    DATE=$(date +%Y%m%d_%H%M%S)
    
    # Backup database
    sudo -u postgres pg_dump soleva_db | gzip > "$BACKUP_DIR/db_backup_pre_deploy_$DATE.sql.gz"
    
    # Backup media files
    if [[ -d "$BACKEND_DIR/media" ]]; then
        tar -czf "$BACKUP_DIR/media_backup_pre_deploy_$DATE.tar.gz" -C "$BACKEND_DIR" media/
    fi
    
    log "✅ Backup completed: $DATE"
}

update_backend() {
    log "Updating backend..."
    
    cd "$BACKEND_DIR"
    
    # Pull latest changes
    git pull origin main || error "Failed to pull backend changes"
    
    # Activate virtual environment
    source venv/bin/activate || error "Failed to activate virtual environment"
    
    # Install/update dependencies
    pip install -r requirements.txt || error "Failed to install Python dependencies"
    
    # Run migrations
    python manage.py migrate || error "Database migration failed"
    
    # Collect static files
    python manage.py collectstatic --noinput || error "Failed to collect static files"
    
    # Check for any issues
    python manage.py check || error "Django check failed"
    
    log "✅ Backend updated successfully"
}

update_frontend() {
    log "Updating frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Pull latest changes
    git pull origin main || error "Failed to pull frontend changes"
    
    # Install dependencies
    npm ci || error "Failed to install Node.js dependencies"
    
    # Build production version
    npm run build || error "Frontend build failed"
    
    log "✅ Frontend updated successfully"
}

restart_services() {
    log "Restarting services..."
    
    # Restart backend services
    systemctl restart gunicorn || error "Failed to restart Gunicorn"
    systemctl restart celery || error "Failed to restart Celery"
    
    # Reload 
    nginx -t || error "Nginx configuration test failed"
    systemctl reload nginx || error "Failed to reload Nginx"
    
    # Check service status
    services=("nginx" "postgresql" "redis-server" "gunicorn" "celery")
    for service in "${services[@]}"; do
        if ! systemctl is-active --quiet "$service"; then
            error "Service $service is not running"
        fi
    done
    
    log "✅ All services restarted successfully"
}

run_health_checks() {
    log "Running health checks..."
    
    # Check if backend is responding
    if ! curl -f http://localhost:8000/api/health/ &> /dev/null; then
        warn "Backend health check failed"
    else
        log "✅ Backend health check passed"
    fi
    
    # Check if frontend is accessible
    if ! curl -f http://localhost/ &> /dev/null; then
        warn "Frontend health check failed"
    else
        log "✅ Frontend health check passed"
    fi
    
    # Check database connection
    cd "$BACKEND_DIR"
    source venv/bin/activate
    if ! python manage.py dbshell -c "\q" 2>/dev/null; then
        warn "Database connection check failed"
    else
        log "✅ Database connection check passed"
    fi
    
    # Check Redis connection
    if ! redis-cli ping &> /dev/null; then
        warn "Redis connection check failed"
    else
        log "✅ Redis connection check passed"
    fi
}

cleanup() {
    log "Cleaning up..."
    
    # Remove old log files (older than 30 days)
    find /var/log -name "*soleva*" -type f -mtime +30 -delete 2>/dev/null || true
    
    # Clean old backups (older than 7 days)
    find "$BACKUP_DIR" -name "*.gz" -type f -mtime +7 -delete 2>/dev/null || true
    
    # Clean npm cache
    npm cache clean --force 2>/dev/null || true
    
    # Clean pip cache
    pip cache purge 2>/dev/null || true
    
    log "✅ Cleanup completed"
}

show_status() {
    echo ""
    echo "📊 Deployment Status"
    echo "===================="
    
    # Service status
    services=("nginx" "postgresql" "redis-server" "gunicorn" "celery")
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            echo -e "✅ $service: ${GREEN}Running${NC}"
        else
            echo -e "❌ $service: ${RED}Not Running${NC}"
        fi
    done
    
    # Disk usage
    echo ""
    echo "💾 Disk Usage:"
    df -h / | tail -1 | awk '{print "   Root: " $5 " used (" $3 "/" $2 ")"}'
    
    # Memory usage
    echo ""
    echo "🧠 Memory Usage:"
    free -h | grep "Mem:" | awk '{print "   Memory: " $3 "/" $2 " (" int($3/$2 * 100) "%)"}'
    
    # Load average
    echo ""
    echo "⚡ Load Average:"
    uptime | awk -F'load average:' '{print "   " $2}'
    
    echo ""
    log "🎉 Deployment completed successfully!"
    echo "🌐 Your site should be available at: https://solevaeg.com"
}

# Main deployment process
main() {
    log "Starting deployment process..."
    
    check_prerequisites
    backup_database
    update_backend
    update_frontend
    restart_services
    run_health_checks
    cleanup
    show_status
    
    log "Deployment completed at $(date)"
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "backup")
        backup_database
        ;;
    "backend")
        update_backend
        restart_services
        ;;
    "frontend")
        update_frontend
        systemctl reload nginx
        ;;
    "health")
        run_health_checks
        ;;
    "status")
        show_status
        ;;
    "help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  deploy    - Full deployment (default)"
        echo "  backup    - Create backup only"
        echo "  backend   - Update backend only"
        echo "  frontend  - Update frontend only"
        echo "  health    - Run health checks"
        echo "  status    - Show system status"
        echo "  help      - Show this help"
        ;;
    *)
        error "Unknown command: $1. Use '$0 help' for usage information."
        ;;
esac
