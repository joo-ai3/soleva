#!/bin/bash
# Quick fix for Soleva backend migration issues
# Addresses static directory and migration order without full reset

set -e

echo "🚀 QUICK BACKEND FIX"
echo "===================="

# Step 1: Create static directory
echo "📁 Step 1: Creating static directory..."
docker run --rm -v "$(pwd)/soleva back end:/app" -w /app python:3.11-slim bash -c "
mkdir -p /app/static
mkdir -p /app/staticfiles
mkdir -p /app/media
mkdir -p /app/logs
echo 'Static directories created'
"

# Step 2: Stop backend container
echo "🛑 Step 2: Stopping backend container..."
docker compose stop backend

# Step 3: Remove only problematic migration files
echo "🧹 Step 3: Cleaning migration files..."
find "soleva back end" -path "*/migrations/*.py" -not -name "__init__.py" -delete

# Step 4: Start backend and recreate migrations in order
echo "🔄 Step 4: Starting backend and fixing migrations..."
docker compose up -d backend

echo "⏳ Step 5: Waiting for backend to be ready..."
sleep 15

echo "📝 Step 6: Creating migrations in correct order..."
docker compose exec backend python manage.py makemigrations users
docker compose exec backend python manage.py makemigrations

echo "⚡ Step 7: Applying migrations in correct order..."
docker compose exec backend python manage.py migrate auth
docker compose exec backend python manage.py migrate contenttypes
docker compose exec backend python manage.py migrate sessions
docker compose exec backend python manage.py migrate users
docker compose exec backend python manage.py migrate admin
docker compose exec backend python manage.py migrate

echo "📦 Step 8: Collecting static files..."
docker compose exec backend python manage.py collectstatic --noinput

echo ""
echo "✅ BACKEND QUICK FIX COMPLETED!"
echo "==============================="

echo ""
echo "📊 Check status:"
echo "docker compose ps"

echo ""
echo "🔍 View logs:"
echo "docker compose logs backend"

echo ""
echo "🌐 Test API:"
echo "curl http://localhost/api/health/"

echo ""
echo "⚠️  Note: If this doesn't work, run the full reset script:"
echo "./fix-migration-issues.sh"
