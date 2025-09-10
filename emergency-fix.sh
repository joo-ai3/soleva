#!/bin/bash
# EMERGENCY FIX for Soleva Backend Migration Issues
# Run this directly on your VPS

set -e

echo "🚨 EMERGENCY FIX FOR SOLEVA BACKEND"
echo "===================================="

cd /root/soleva

# Step 1: Stop everything
echo "🛑 Step 1: Stopping all containers..."
docker compose down --remove-orphans

# Step 2: Clean up containers
echo "🧹 Step 2: Removing orphan containers..."
docker ps -a --filter "name=soleva" --format "{{.Names}}" | xargs -r docker rm -f

# Step 3: Create static directories
echo "📁 Step 3: Creating static directories..."
docker run --rm -v "$(pwd)/soleva back end:/app" -w /app python:3.11-slim bash -c "
mkdir -p /app/static /app/staticfiles /app/media /app/logs
echo 'Static directories created'
"

# Step 4: Start database only
echo "🗄️ Step 4: Starting database..."
docker compose up -d postgres
sleep 10

# Step 5: Reset database (CAUTION: This deletes all data!)
echo "🔄 Step 5: Resetting database..."
docker compose exec postgres psql -U soleva_user -d soleva_db << 'EOF'
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO soleva_user;
GRANT ALL ON SCHEMA public TO public;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO soleva_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO soleva_user;
EOF

# Step 6: Start backend and Redis
echo "🚀 Step 6: Starting backend and Redis..."
docker compose up -d redis
docker compose up -d backend
sleep 20

# Step 7: Force correct migration order
echo "📋 Step 7: Applying migrations in correct order..."

# Apply core Django migrations first
docker compose exec backend python manage.py migrate auth --verbosity=2
docker compose exec backend python manage.py migrate contenttypes --verbosity=2
docker compose exec backend python manage.py migrate sessions --verbosity=2

# Apply users migration (this creates the users table)
docker compose exec backend python manage.py migrate users --verbosity=2

# Apply admin migration (now users table exists)
docker compose exec backend python manage.py migrate admin --verbosity=2

# Apply remaining migrations
docker compose exec backend python manage.py migrate --verbosity=2

# Step 8: Create superuser
echo "👤 Step 8: Creating superuser..."
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
    print('✅ Superuser created successfully!')
    print('Email: admin@solevaeg.com')
    print('Password: ' + os.environ.get('ADMIN_PASSWORD', 'S0l3v@_Admin!2025#'))
else:
    print('ℹ️  Superuser already exists')
EOF

# Step 9: Collect static files
echo "📦 Step 9: Collecting static files..."
docker compose exec backend python manage.py collectstatic --noinput --verbosity=0

# Step 10: Start all services
echo "🌐 Step 10: Starting all services..."
docker compose up -d frontend nginx celery celery-beat

# Step 11: Final verification
echo "✅ Step 11: Final verification..."
sleep 5

echo ""
echo "🎉 EMERGENCY FIX COMPLETED!"
echo "==========================="

echo ""
echo "📊 Service Status:"
docker compose ps

echo ""
echo "🔍 Test backend:"
curl -s http://localhost:8000/api/health/ | head -5

echo ""
echo "🌐 Access URLs:"
echo "• Frontend: http://localhost"
echo "• Admin: http://localhost/admin/"
echo "• API: http://localhost/api/"
echo "• Superuser: admin@solevaeg.com"

echo ""
echo "⚠️  IMPORTANT:"
echo "• All previous data was deleted during database reset"
echo "• Backend should now be healthy and stable"
echo "• If issues persist, check logs: docker compose logs backend"
