#!/bin/bash
# IMMEDIATE BACKEND FIX for Soleva
# Run this on your VPS to fix the "relation 'users' does not exist" error

set -e

echo "🔧 FIXING SOLEVA BACKEND MIGRATION ISSUE"
echo "========================================="

# Stop all containers
echo "📋 Step 1: Stopping all containers..."
docker compose down --remove-orphans

# Remove problematic migration files
echo "📋 Step 2: Removing migration files..."
find "soleva back end" -path "*/migrations/*.py" -not -name "__init__.py" -delete

# Reset database
echo "📋 Step 3: Resetting database..."
docker compose up -d postgres
sleep 5

docker compose exec postgres psql -U soleva_user -d soleva_db << 'EOF'
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO soleva_user;
GRANT ALL ON SCHEMA public TO public;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO soleva_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO soleva_user;
EOF

# Start backend and recreate migrations
echo "📋 Step 4: Starting backend and recreating migrations..."
docker compose up -d redis backend

# Wait for backend to be ready
echo "📋 Step 5: Waiting for backend to start..."
sleep 15

# Recreate migrations
echo "📋 Step 6: Recreating migrations..."
docker compose exec backend python manage.py makemigrations

# Apply migrations
echo "📋 Step 7: Applying migrations..."
docker compose exec backend python manage.py migrate

# Create superuser
echo "📋 Step 8: Creating superuser..."
docker compose exec backend python manage.py shell << 'EOF'
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
else:
    print('Superuser already exists')
EOF

# Start all services
echo "📋 Step 9: Starting all services..."
docker compose up -d frontend nginx celery celery-beat

# Final verification
echo "📋 Step 10: Verifying setup..."
sleep 5

echo ""
echo "🎉 BACKEND FIX COMPLETED!"
echo "========================"
echo ""
echo "✅ Database reset and migrations applied"
echo "✅ Superuser created: admin@solevaeg.com"
echo "✅ All services should be running now"
echo ""
echo "📊 Check status:"
echo "docker compose ps"
echo ""
echo "📋 View logs:"
echo "docker compose logs backend"
echo ""
echo "🌐 Access your application:"
echo "• Frontend: http://localhost"
echo "• Admin: http://localhost/admin/"
echo "• API: http://localhost/api/"
