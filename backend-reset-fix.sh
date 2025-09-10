#!/bin/bash
# Backend Reset and Migration Fix Script for Soleva
# This script completely resets the backend and fixes migration issues

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

# Function to stop all services
stop_services() {
    print_status "Stopping all services..."
    docker compose down --remove-orphans 2>/dev/null || print_warning "No running services to stop"
}

# Function to remove migration files
remove_migrations() {
    print_status "Removing existing migration files..."

    # Define apps with migrations
    apps=("users" "products" "cart" "orders" "coupons" "notifications" "shipping" "payments" "tracking" "offers" "accounting" "otp" "website_management")

    for app in "${apps[@]}"; do
        migration_dir="soleva back end/$app/migrations"
        if [ -d "$migration_dir" ]; then
            print_info "Removing migrations for $app..."

            # Remove all migration files except __init__.py
            find "$migration_dir" -name "*.py" -not -name "__init__.py" -delete 2>/dev/null || true

            # Verify cleanup
            migration_count=$(find "$migration_dir" -name "*.py" -not -name "__init__.py" | wc -l)
            if [ "$migration_count" -eq 0 ]; then
                print_status "✅ Cleaned migrations for $app"
            else
                print_warning "⚠️  Some migration files may remain for $app"
            fi
        else
            print_warning "Migration directory not found for $app: $migration_dir"
        fi
    done

    print_status "Migration cleanup completed!"
}

# Function to reset PostgreSQL database
reset_database() {
    print_status "Resetting PostgreSQL database..."

    # Start only PostgreSQL
    print_info "Starting PostgreSQL..."
    docker compose up -d postgres

    # Wait for PostgreSQL to be ready
    print_info "Waiting for PostgreSQL to be ready..."
    max_attempts=30
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker compose exec -T postgres pg_isready -U soleva_user -d soleva_db >/dev/null 2>&1; then
            print_status "PostgreSQL is ready!"
            break
        fi

        print_info "Waiting... (attempt $attempt/$max_attempts)"
        sleep 3
        ((attempt++))
    done

    if [ $attempt -gt $max_attempts ]; then
        print_error "PostgreSQL failed to start properly"
        exit 1
    fi

    # Reset database schema
    print_info "Resetting database schema..."
    docker compose exec -T postgres psql -U soleva_user -d soleva_db << EOF
-- Drop and recreate public schema
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- Grant permissions
GRANT ALL ON SCHEMA public TO soleva_user;
GRANT ALL ON SCHEMA public TO public;

-- Set default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO soleva_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO soleva_user;
EOF

    print_status "✅ Database reset completed!"
}

# Function to start backend
start_backend() {
    print_status "Starting backend container..."

    # Start Redis as well since backend depends on it
    print_info "Starting Redis..."
    docker compose up -d redis

    # Wait for Redis
    print_info "Waiting for Redis..."
    max_attempts=20
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker compose exec -T redis redis-cli -a "Redis@2025" ping | grep -q PONG; then
            print_status "Redis is ready!"
            break
        fi

        print_info "Waiting for Redis... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done

    if [ $attempt -gt $max_attempts ]; then
        print_warning "Redis may not be ready, but continuing..."
    fi

    # Start backend
    print_info "Starting backend container..."
    docker compose up -d backend

    # Wait for backend to be ready
    print_info "Waiting for backend to start..."
    sleep 10

    print_status "✅ Backend container started!"
}

# Function to recreate and apply migrations
recreate_migrations() {
    print_status "Recreating and applying migrations..."

    # Make migrations
    print_info "Creating new migrations..."
    if docker compose exec -T backend python manage.py makemigrations; then
        print_status "✅ Makemigrations completed successfully"
    else
        print_error "❌ Makemigrations failed"
        docker compose logs backend
        exit 1
    fi

    # Apply migrations
    print_info "Applying migrations..."
    if docker compose exec -T backend python manage.py migrate; then
        print_status "✅ Migrations applied successfully"
    else
        print_error "❌ Migration failed"
        docker compose logs backend
        exit 1
    fi
}

# Function to create superuser
create_superuser() {
    print_status "Creating superuser..."

    # Create superuser non-interactively
    docker compose exec -T backend python manage.py shell << EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()

# Check if superuser already exists
if not User.objects.filter(email='admin@solevaeg.com').exists():
    User.objects.create_superuser(
        email='admin@solevaeg.com',
        password=os.environ.get('ADMIN_PASSWORD', 'S0l3v@_Admin!2025#'),
        first_name='Admin',
        last_name='User'
    )
    print('✅ Superuser created successfully')
    print('Email: admin@solevaeg.com')
    print('Password: ' + os.environ.get('ADMIN_PASSWORD', 'S0l3v@_Admin!2025#'))
else:
    print('ℹ️  Superuser already exists')
EOF

    print_status "✅ Superuser setup completed!"
}

# Function to verify everything is working
verify_setup() {
    print_status "Verifying setup..."

    echo ""
    print_status "Container Status:"
    docker compose ps

    echo ""
    print_status "Testing backend health:"
    if curl -f http://localhost:8000/api/health/ >/dev/null 2>&1; then
        print_status "✅ Backend API is responding"
    else
        print_warning "⚠️  Backend API is not responding yet"
        print_info "This is normal if the backend is still starting up"
    fi

    echo ""
    print_status "Recent backend logs:"
    docker compose logs --tail=20 backend

    echo ""
    print_status "Database tables check:"
    docker compose exec -T backend python manage.py shell << EOF
from django.db import connection
from django.core.management.color import no_style

style = no_style()
sql = connection.ops.sql_table_creation_suffix()
with connection.cursor() as cursor:
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public';")
    tables = cursor.fetchall()

print(f"📊 Found {len(tables)} tables in database:")
for table in tables[:10]:  # Show first 10 tables
    print(f"  - {table[0]}")
if len(tables) > 10:
    print(f"  ... and {len(tables) - 10} more tables")
EOF
}

# Function to show summary
show_summary() {
    echo ""
    print_status "🎉 BACKEND RESET COMPLETED!"
    echo "=================================="

    echo ""
    print_status "What was done:"
    echo "  ✅ Removed all existing migration files"
    echo "  ✅ Reset PostgreSQL database (dropped and recreated public schema)"
    echo "  ✅ Started backend container with dependencies"
    echo "  ✅ Recreated and applied all migrations"
    echo "  ✅ Created superuser account"

    echo ""
    print_status "Access your application:"
    echo "  • Backend API: http://localhost:8000/api/"
    echo "  • Admin Panel: http://localhost/admin/"
    echo "  • Superuser Email: admin@solevaeg.com"
    echo "  • Superuser Password: S0l3v@_Admin!2025#"

    echo ""
    print_status "Useful commands:"
    echo "  • View logs: docker compose logs -f backend"
    echo "  • Restart backend: docker compose restart backend"
    echo "  • Check status: docker compose ps"
    echo "  • Stop all: docker compose down"

    echo ""
    print_warning "⚠️  IMPORTANT NOTES:"
    echo "  • All previous data has been removed from the database"
    echo "  • You may need to restart other services (frontend, nginx) if needed"
    echo "  • The static files warning is expected and can be ignored for now"
}

# Main script execution
main() {
    echo "🔄 SOLEVA BACKEND RESET & MIGRATION FIX"
    echo "======================================="

    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        echo "Soleva Backend Reset and Migration Fix Script"
        echo ""
        echo "This script will:"
        echo "  • Stop all services"
        echo "  • Remove all existing migration files"
        echo "  • Reset PostgreSQL database (DROPS ALL DATA)"
        echo "  • Start backend container"
        echo "  • Recreate and apply migrations"
        echo "  • Create superuser"
        echo "  • Verify everything is working"
        echo ""
        echo "⚠️  WARNING: This will DELETE ALL existing data in the database!"
        echo ""
        echo "Usage: $0 [options]"
        echo "Options:"
        echo "  --help, -h    Show this help message"
        echo "  --dry-run     Show what would be done without executing"
        echo ""
        return
    fi

    if [ "$1" = "--dry-run" ]; then
        echo "🔍 DRY RUN MODE - Showing what would be done:"
        echo ""
        echo "1. Stop all services"
        echo "2. Remove migration files from:"
        echo "   - users, products, cart, orders, coupons, notifications"
        echo "   - shipping, payments, tracking, offers, accounting, otp"
        echo "   - website_management"
        echo "3. Reset PostgreSQL database (DROP SCHEMA public CASCADE)"
        echo "4. Start backend container"
        echo "5. Run: python manage.py makemigrations"
        echo "6. Run: python manage.py migrate"
        echo "7. Create superuser: admin@solevaeg.com"
        echo ""
        print_warning "⚠️  This would DELETE ALL existing data!"
        return
    fi

    # Safety confirmation
    echo ""
    print_warning "⚠️  WARNING: This will DELETE ALL existing data in the database!"
    echo ""
    read -p "Are you sure you want to continue? (type 'yes' to confirm): " confirm

    if [ "$confirm" != "yes" ]; then
        print_info "Operation cancelled by user."
        exit 0
    fi

    # Execute all steps
    check_docker
    stop_services
    remove_migrations
    reset_database
    start_backend
    recreate_migrations
    create_superuser
    verify_setup
    show_summary
}

# Run main function
main "$@"
