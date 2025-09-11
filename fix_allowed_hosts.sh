#!/bin/bash

# Fix ALLOWED_HOSTS issue for Soleva deployment
echo "🔧 Fixing ALLOWED_HOSTS issue..."

# Navigate to project directory
cd /home/ubuntu/soleva

# Stop the backend container
echo "Stopping backend container..."
docker compose stop backend

# Rebuild the backend container to ensure latest changes are applied
echo "Rebuilding backend container..."
docker compose build backend

# Start the backend container
echo "Starting backend container..."
docker compose up -d backend

# Check if everything is working
echo "Checking container status..."
docker compose ps backend

# Check recent logs to see if ALLOWED_HOSTS is working
echo "📋 Checking recent backend logs..."
sleep 5
docker compose logs --tail=30 backend

echo "✅ Backend container rebuilt and restarted. Check if the DisallowedHost errors are gone."
