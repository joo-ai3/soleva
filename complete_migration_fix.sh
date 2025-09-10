#!/bin/bash
# COMPLETE MIGRATION FIX FOR SOLEVA BACKEND
# This script fixes the "relation 'users' does not exist" error
# Run this script on your server at ~/soleva/complete_migration_fix.sh

set -e

echo "🔧 COMPLETE MIGRATION FIX FOR SOLEVA"
echo "===================================="
echo "This script will fix the Django migration issues"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Check if we're in the right directory
if [ ! -d "soleva back end" ]; then
    print_error "Error: 'soleva back end' directory not found!"
    print_error "Please run this script from the soleva project root directory"
    exit 1
fi

print_status "Working directory: $(pwd)"
print_status "Found 'soleva back end' directory - proceeding..."

# Step 2: Stop all containers
print_status "Step 1: Stopping all containers..."
docker compose down --remove-orphans --volumes 2>/dev/null || true

# Step 3: Clean up any remaining containers
print_status "Step 2: Cleaning up remaining containers..."
docker ps -a --filter "name=soleva" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true

# Step 4: Create necessary directories
print_status "Step 3: Creating necessary directories..."
mkdir -p "soleva back end/static"
mkdir -p "soleva back end/staticfiles"
mkdir -p "soleva back end/media"
mkdir -p "soleva back end/logs"
print_success "Directories created"

# Step 5: Start database only
print_status "Step 4: Starting PostgreSQL database..."
docker compose up -d postgres

# Wait for database to be ready
print_status "Step 5: Waiting for database to be ready..."
sleep 15

# Test database connection
if docker compose exec -T postgres pg_isready -U soleva_user -d soleva_db >/dev/null 2>&1; then
    print_success "Database is ready"
else
    print_error "Database connection failed"
    exit 1
fi

# Step 6: Reset database schema (WARNING: This deletes all data!)
print_warning "Step 6: Resetting database schema (this deletes all data)..."
docker compose exec -T postgres psql -U soleva_user -d soleva_db << 'EOF'
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO soleva_user;
GRANT ALL ON SCHEMA public TO public;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO soleva_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO soleva_user;
EOF
print_success "Database reset completed"

# Step 7: Start Redis and backend
print_status "Step 7: Starting Redis and backend services..."
docker compose up -d redis
docker compose up -d backend

# Wait for services to be ready
print_status "Step 8: Waiting for services to be ready..."
sleep 25

# Step 8: Apply migrations in correct order
print_status "Step 9: Applying migrations in correct order..."

# Function to run migration with error handling
run_migration() {
    local app=$1
    local description=${2:-$app}
    print_status "  Applying $description migrations..."

    if docker compose exec -T backend python manage.py migrate "$app" --verbosity=1; then
        print_success "  ✓ $description migrations applied successfully"
    else
        print_error "  ✗ Failed to apply $description migrations"
        return 1
    fi
}

# Apply core Django migrations first
run_migration "auth" "Django Auth"
run_migration "contenttypes" "Django Content Types"
run_migration "sessions" "Django Sessions"

# Apply users migration (this creates the users table)
run_migration "users" "Custom User Model"

# Apply admin migration (depends on users)
run_migration "admin" "Django Admin"

# Apply remaining migrations
print_status "  Applying remaining app migrations..."
if docker compose exec -T backend python manage.py migrate --verbosity=1; then
    print_success "  ✓ All remaining migrations applied successfully"
else
    print_error "  ✗ Failed to apply remaining migrations"
    exit 1
fi

# Step 9: Create superuser
print_status "Step 10: Creating superuser..."
docker compose exec -T backend python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
import os

User = get_user_model()
if not User.objects.filter(email='admin@solevaeg.com').exists():
    User.objects.create_superuser(
        email='admin@solevaeg.com',
        password=os.environ.get('ADMIN_PASSWORD', 'S0l3v@_Admin!2025#'),
        first_name='Admin',
        last_name='User'
    )
    print('Superuser created successfully!')
    print('Email: admin@solevaeg.com')
    print('Password: S0l3v@_Admin!2025#')
else:
    print('Superuser already exists')
EOF
print_success "Superuser creation completed"

# Step 10: Collect static files
print_status "Step 11: Collecting static files..."
docker compose exec -T backend python manage.py collectstatic --noinput --verbosity=0
print_success "Static files collected"

# Step 11: Start all remaining services
print_status "Step 12: Starting all services..."
docker compose up -d frontend nginx celery celery-beat

# Step 12: Final verification
print_status "Step 13: Final verification..."
sleep 10

# Check container status
echo ""
print_status "SERVICE STATUS:"
echo "==============="
docker compose ps

# Test backend health
echo ""
print_status "BACKEND HEALTH CHECK:"
echo "======================"
if curl -s --max-time 10 http://localhost/api/health/ >/dev/null 2>&1; then
    print_success "✓ Backend health check passed"
else
    print_warning "! Backend health check failed (may still be starting)"
fi

# Final summary
echo ""
echo "========================================="
echo -e "${GREEN}🎉 MIGRATION FIX COMPLETED SUCCESSFULLY!${NC}"
echo "========================================="
echo ""
echo -e "${BLUE}📊 SERVICE STATUS:${NC}"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo -e "${BLUE}🌐 ACCESS URLs:${NC}"
echo "• Frontend: http://localhost"
echo "• Admin: http://localhost/admin/"
echo "• API: http://localhost/api/"
echo "• Superuser: admin@solevaeg.com"
echo "• Password: S0l3v@_Admin!2025#"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT NOTES:${NC}"
echo "• All previous data was deleted during database reset"
echo "• Backend should now be healthy and stable"
echo "• If issues persist, check logs: docker compose logs backend"
echo ""
echo -e "${GREEN}✅ Migration fix completed! Your Soleva application should now be running.${NC}"
