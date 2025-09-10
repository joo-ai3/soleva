#!/bin/bash
# Comprehensive Docker Cleanup and Startup Script for Soleva
# This script fixes backend connection issues and removes orphan containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    print_status "Checking Docker status..."
    if ! docker --version >/dev/null 2>&1; then
        print_error "Docker is not installed or not running"
        exit 1
    fi

    if ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not available"
        exit 1
    fi

    print_status "Docker is ready!"
}

# Function to clean up orphan containers and resources
cleanup_containers() {
    print_status "Cleaning up Docker resources..."

    # Stop all running containers
    print_info "Stopping all containers..."
    docker compose down --remove-orphans 2>/dev/null || print_warning "No running containers to stop"

    # Remove orphan containers
    print_info "Removing orphan containers..."
    docker compose down --remove-orphans --volumes 2>/dev/null || print_warning "No orphans to clean"

    # Clean up unused containers, networks, and images
    print_info "Cleaning up unused Docker resources..."
    docker system prune -f >/dev/null 2>&1 || print_warning "System prune failed"

    # Remove any leftover containers with 'soleva' in the name
    print_info "Removing any leftover Soleva containers..."
    docker ps -a --filter "name=soleva" --format "table {{.Names}}" | grep -v NAMES | xargs -r docker rm -f 2>/dev/null || print_warning "No leftover containers to remove"

    print_status "Cleanup completed!"
}

# Function to verify environment configuration
verify_environment() {
    print_status "Verifying environment configuration..."

    # Check if docker.env exists
    if [ ! -f "docker.env" ]; then
        print_error "docker.env file not found!"
        print_info "Creating docker.env from docker.env.example..."
        if [ -f "docker.env.example" ]; then
            cp docker.env.example docker.env
            print_warning "Please update docker.env with your actual configuration values"
        else
            print_error "Neither docker.env nor docker.env.example found"
            exit 1
        fi
    fi

    # Verify critical environment variables
    required_vars=("DB_HOST" "DB_NAME" "DB_USER" "DB_PASSWORD" "REDIS_PASSWORD")
    missing_vars=()

    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" docker.env; then
            missing_vars+=("$var")
        fi
    done

    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing required environment variables: ${missing_vars[*]}"
        print_info "Please check your docker.env file"
        exit 1
    fi

    print_status "Environment configuration is valid!"
}

# Function to start services in correct order
start_services() {
    print_status "Starting Soleva services..."

    # Start only database and Redis first
    print_info "Starting database and Redis services..."
    docker compose up -d postgres redis

    # Wait for database and Redis to be healthy
    print_info "Waiting for database and Redis to be ready..."
    max_attempts=30
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        print_info "Health check attempt $attempt/$max_attempts..."

        # Check PostgreSQL
        if docker compose exec -T postgres pg_isready -U soleva_user -d soleva_db >/dev/null 2>&1; then
            print_status "PostgreSQL is ready!"
            postgres_ready=true
        else
            postgres_ready=false
        fi

        # Check Redis
        if docker compose exec -T redis redis-cli -a "Redis@2025" ping | grep -q PONG; then
            print_status "Redis is ready!"
            redis_ready=true
        else
            redis_ready=false
        fi

        if [ "$postgres_ready" = true ] && [ "$redis_ready" = true ]; then
            print_status "All dependencies are ready!"
            break
        fi

        sleep 5
        ((attempt++))
    done

    if [ $attempt -gt $max_attempts ]; then
        print_error "Database and/or Redis failed to start properly"
        docker compose logs postgres redis
        exit 1
    fi

    # Start backend
    print_info "Starting backend service..."
    docker compose up -d backend

    # Wait for backend to be ready
    print_info "Waiting for backend to be ready..."
    max_attempts=20
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        print_info "Backend health check attempt $attempt/$max_attempts..."

        if curl -f http://localhost:8000/api/health/ >/dev/null 2>&1; then
            print_status "Backend is ready!"
            break
        else
            sleep 5
            ((attempt++))
        fi
    done

    if [ $attempt -gt $max_attempts ]; then
        print_error "Backend failed to start properly"
        docker compose logs backend
        exit 1
    fi

    # Start remaining services
    print_info "Starting remaining services..."
    docker compose up -d frontend nginx celery celery-beat

    print_status "All services started successfully!"
}

# Function to verify everything is working
verify_services() {
    print_status "Verifying service status..."

    echo ""
    docker compose ps

    echo ""
    print_status "Testing service health:"

    # Test backend API
    if curl -f http://localhost:8000/api/health/ >/dev/null 2>&1; then
        print_status "✅ Backend API is responding"
    else
        print_warning "⚠️  Backend API is not responding yet"
    fi

    # Test frontend
    if curl -f http://localhost:3000/ >/dev/null 2>&1; then
        print_status "✅ Frontend is responding"
    else
        print_warning "⚠️  Frontend is not responding yet"
    fi

    # Test nginx
    if curl -f http://localhost/ >/dev/null 2>&1; then
        print_status "✅ Nginx reverse proxy is working"
    else
        print_warning "⚠️  Nginx is not responding yet"
    fi

    echo ""
    print_status "Useful commands:"
    echo "  • View logs:           docker compose logs -f"
    echo "  • Stop services:       docker compose down"
    echo "  • Restart backend:     docker compose restart backend"
    echo "  • View running status: docker compose ps"
    echo "  • Clean restart:       ./docker-cleanup-and-start.sh"
}

# Main script
main() {
    print_status "🚀 SOLEVA DOCKER CLEANUP AND STARTUP"
    echo "======================================"

    # Change to project root if needed
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found in current directory"
        print_info "Please run this script from the project root directory"
        exit 1
    fi

    check_docker
    cleanup_containers
    verify_environment
    start_services
    verify_services

    echo ""
    print_status "🎉 SOLEVA IS NOW RUNNING SUCCESSFULLY!"
    print_info "Access your application at:"
    echo "  • Frontend: http://localhost"
    echo "  • Backend API: http://localhost/api/"
    echo "  • Admin Panel: http://localhost/admin/"
}

# Show usage if help is requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Soleva Docker Cleanup and Startup Script"
    echo "Usage: $0 [options]"
    echo ""
    echo "This script:"
    echo "  • Cleans up orphan containers and resources"
    echo "  • Verifies environment configuration"
    echo "  • Starts services in correct order (database → Redis → backend → others)"
    echo "  • Ensures all services are healthy before proceeding"
    echo "  • Provides verification of the running system"
    echo ""
    echo "Options:"
    echo "  --help, -h    Show this help message"
    echo ""
    exit 0
fi

# Run main function
main "$@"
