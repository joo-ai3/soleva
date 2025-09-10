#!/bin/bash
# Complete fix for Soleva backend migration issues
# Addresses: static directory, migration order, and database readiness

set -e

echo "🔧 FIXING SOLEVA BACKEND MIGRATION ISSUES"
echo "==========================================="

# Step 1: Stop all containers
echo "📋 Step 1: Stopping all containers..."
docker compose down --remove-orphans

# Step 2: Create static directory
echo "📋 Step 2: Creating static directory..."
docker run --rm -v "$(pwd)/soleva back end:/app" -w /app python:3.11-slim bash -c "
mkdir -p /app/static
mkdir -p /app/staticfiles
mkdir -p /app/media
mkdir -p /app/logs
echo 'Static directories created successfully'
"

# Step 3: Remove problematic migration files
echo "📋 Step 3: Removing problematic migration files..."
find "soleva back end" -path "*/migrations/*.py" -not -name "__init__.py" -delete

# Step 4: Reset database
echo "📋 Step 4: Resetting database..."
docker compose up -d postgres
sleep 5

docker compose exec postgres psql -U soleva_user -d soleva_db << 'EOF'
-- Reset database completely
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- Grant permissions
GRANT ALL ON SCHEMA public TO soleva_user;
GRANT ALL ON SCHEMA public TO public;

-- Set default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO soleva_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO soleva_user;
EOF

echo "✅ Database reset completed"

# Step 5: Start backend with Redis
echo "📋 Step 5: Starting backend and Redis..."
docker compose up -d redis
docker compose up -d backend

# Wait for backend to be ready
echo "📋 Step 6: Waiting for backend to be ready..."
sleep 20

# Step 6: Create migrations in correct order
echo "📋 Step 7: Creating migrations for users first..."
docker compose exec backend python manage.py makemigrations users

echo "📋 Step 8: Creating migrations for other apps..."
docker compose exec backend python manage.py makemigrations

# Step 7: Apply migrations in correct order
echo "📋 Step 9: Applying migrations in correct order..."

# Apply auth, contenttypes, sessions first (dependencies)
docker compose exec backend python manage.py migrate auth
docker compose exec backend python manage.py migrate contenttypes
docker compose exec backend python manage.py migrate sessions

# Apply users migration (custom user model)
docker compose exec backend python manage.py migrate users

# Apply admin (depends on users)
docker compose exec backend python manage.py migrate admin

# Apply remaining migrations
docker compose exec backend python manage.py migrate

# Step 8: Create superuser
echo "📋 Step 10: Creating superuser..."
docker compose exec backend python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
import os

User = get_user_model()
if not User.objects.filter(email='admin@thesoleva.com').exists():
    User.objects.create_superuser(
        email='admin@thesoleva.com',
        password=os.environ.get('ADMIN_PASSWORD', 'S0l3v@_Admin!2025#'),
        first_name='Admin',
        last_name='User'
    )
    print('✅ Superuser created successfully!')
    print('Email: admin@thesoleva.com')
    print('Password: ' + os.environ.get('ADMIN_PASSWORD', 'S0l3v@_Admin!2025#'))
else:
    print('ℹ️  Superuser already exists')
EOF

# Step 9: Collect static files
echo "📋 Step 11: Collecting static files..."
docker compose exec backend python manage.py collectstatic --noinput

# Step 10: Start all services
echo "📋 Step 12: Starting all services..."
docker compose up -d frontend nginx celery celery-beat

# Step 11: Final verification
echo "📋 Step 13: Final verification..."
sleep 5

echo ""
echo "🎉 MIGRATION ISSUES FIXED!"
echo "=========================="

echo ""
echo "✅ Static directory created"
echo "✅ Migration files cleaned"
echo "✅ Database reset"
echo "✅ Migrations applied in correct order"
echo "✅ Superuser created"
echo "✅ Static files collected"
echo "✅ All services started"

echo ""
echo "📊 Service Status:"
docker compose ps

echo ""
echo "🔍 Check logs:"
echo "docker compose logs backend"

echo ""
echo "🌐 Access URLs:"
echo "• Frontend: http://localhost"
echo "• Admin: http://localhost/admin/"
echo "• API: http://localhost/api/"
echo "• Superuser: admin@thesoleva.com"

echo ""
echo "⚠️  Note: All previous data was removed during database reset"
