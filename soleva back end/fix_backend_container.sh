#!/bin/bash
# Comprehensive Backend Container Fix Script
# This script diagnoses and fixes common backend container issues

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main script
main() {
    print_status "Starting Backend Container Diagnostics and Fix"
    echo "=================================================="

    # Check if Docker is available
    if ! command_exists docker; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi

    # Navigate to project root
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

    if [ ! -f "$PROJECT_ROOT/docker-compose.yml" ]; then
        print_error "docker-compose.yml not found in $PROJECT_ROOT"
        exit 1
    fi

    cd "$PROJECT_ROOT"
    print_status "Working directory: $(pwd)"

    # Step 1: Stop all containers
    print_status "Step 1: Stopping all containers..."
    docker compose down || print_warning "Failed to stop containers gracefully"

    # Step 2: Clean up
    print_status "Step 2: Cleaning up Docker resources..."
    docker system prune -f >/dev/null 2>&1 || print_warning "System prune failed"

    # Step 3: Check environment file
    print_status "Step 3: Checking environment configuration..."
    if [ ! -f "docker.env" ]; then
        print_warning "docker.env file not found"
        if [ -f "docker.env.example" ]; then
            print_info "Found docker.env.example - copying to docker.env"
            cp docker.env.example docker.env
            print_warning "Please update docker.env with your actual configuration values"
        else
            print_error "Neither docker.env nor docker.env.example found"
            exit 1
        fi
    else
        print_status "docker.env file found"
    fi

    # Step 4: Rebuild backend container
    print_status "Step 4: Rebuilding backend container..."
    if docker compose build backend; then
        print_status "Backend container rebuilt successfully"
    else
        print_error "Failed to rebuild backend container"
        exit 1
    fi

    # Step 5: Start only database and Redis first
    print_status "Step 5: Starting database and Redis services..."
    if docker compose up -d postgres redis; then
        print_status "Database and Redis started successfully"

        # Wait for services to be ready
        print_info "Waiting for services to be ready..."
        sleep 10

        # Check if services are healthy
        if docker compose ps postgres | grep -q "healthy\|running"; then
            print_status "PostgreSQL is running"
        else
            print_warning "PostgreSQL may not be ready yet"
        fi

        if docker compose ps redis | grep -q "healthy\|running"; then
            print_status "Redis is running"
        else
            print_warning "Redis may not be ready yet"
        fi
    else
        print_error "Failed to start database and Redis"
        exit 1
    fi

    # Step 6: Run migrations manually
    print_status "Step 6: Running database migrations..."

    # Try the automatic migration script first
    if [ -f "soleva back end/fix_migrations.sh" ]; then
        print_info "Using migration fix script..."
        if docker compose run --rm backend bash -c "cd /app && chmod +x fix_migrations.sh && ./fix_migrations.sh"; then
            print_status "Migrations completed successfully using fix script"
        else
            print_warning "Migration fix script failed, trying manual approach..."
        fi
    fi

    # Manual migration approach
    print_info "Running manual migrations in correct order..."

    MIGRATION_COMMANDS=(
        "python manage.py migrate auth"
        "python manage.py migrate contenttypes"
        "python manage.py migrate sessions"
        "python manage.py migrate users"
        "python manage.py migrate admin"
        "python manage.py migrate shipping"
        "python manage.py migrate otp"
        "python manage.py migrate products"
        "python manage.py migrate offers"
        "python manage.py migrate cart"
        "python manage.py migrate coupons"
        "python manage.py migrate notifications"
        "python manage.py migrate accounting"
        "python manage.py migrate payments"
        "python manage.py migrate tracking"
        "python manage.py migrate website_management"
        "python manage.py migrate orders"
    )

    for cmd in "${MIGRATION_COMMANDS[@]}"; do
        print_info "Running: $cmd"
        if docker compose run --rm backend bash -c "cd /app && $cmd"; then
            print_status "✓ $cmd completed"
        else
            print_warning "✗ $cmd failed - continuing..."
        fi
    done

    # Step 7: Collect static files
    print_status "Step 7: Collecting static files..."
    docker compose run --rm backend bash -c "cd /app && python manage.py collectstatic --noinput" || print_warning "Static files collection failed"

    # Step 8: Start all services
    print_status "Step 8: Starting all services..."
    if docker compose up -d; then
        print_status "All services started successfully"
    else
        print_error "Failed to start all services"
        exit 1
    fi

    # Step 9: Check service status
    print_status "Step 9: Checking service status..."
    echo ""
    docker compose ps

    # Step 10: Test backend health
    print_status "Step 10: Testing backend health..."
    sleep 5

    if curl -f http://localhost/api/health/ >/dev/null 2>&1; then
        print_status "✅ Backend is healthy and responding"
    else
        print_warning "⚠️  Backend health check failed - it may still be starting up"
        print_info "Check logs with: docker compose logs backend"
    fi

    # Step 11: Show useful commands
    echo ""
    print_status "Useful commands for monitoring:"
    echo "  • Check logs:           docker compose logs backend"
    echo "  • Check all logs:       docker compose logs"
    echo "  • Restart backend:      docker compose restart backend"
    echo "  • View running services: docker compose ps"
    echo "  • Stop all services:    docker compose down"
    echo "  • Start all services:   docker compose up -d"

    echo ""
    print_status "🎉 BACKEND CONTAINER FIX COMPLETED!"
    print_info "If you still experience issues, check the logs and ensure all environment variables are properly set."

    # Final status
    echo ""
    print_status "Final service status:"
    docker compose ps --format "table {{.Name}}\t{{.Service}}\t{{.Status}}\t{{.Ports}}"
}

# Show usage if help is requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Soleva Backend Container Fix Script"
    echo "Usage: $0 [options]"
    echo ""
    echo "This script diagnoses and fixes common backend container issues:"
    echo "  • Stops and cleans up containers"
    echo "  • Rebuilds backend container with fresh image"
    echo "  • Starts database and Redis services"
    echo "  • Runs migrations in correct order"
    echo "  • Collects static files"
    echo "  • Starts all services"
    echo "  • Performs health checks"
    echo ""
    echo "Options:"
    echo "  --help, -h    Show this help message"
    echo ""
    exit 0
fi

# Run main function
main "$@"
