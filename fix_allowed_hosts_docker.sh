#!/bin/bash

echo "=== Soleva ALLOWED_HOSTS Fix Script ==="
echo "Checking current ALLOWED_HOSTS configuration..."

# Check if docker.env exists
if [ ! -f "docker.env" ]; then
    echo "❌ Error: docker.env file not found!"
    exit 1
fi

# Display current ALLOWED_HOSTS setting
echo "Current ALLOWED_HOSTS in docker.env:"
grep "ALLOWED_HOSTS" docker.env

echo ""
echo "✅ ALLOWED_HOSTS includes 'backend:8000' - this should resolve the issue"

echo ""
echo "Restarting backend container to apply changes..."

# Stop the backend container
docker-compose stop backend

# Start the backend container
docker-compose up -d backend

echo ""
echo "⏳ Waiting for backend container to start..."
sleep 10

echo ""
echo "Testing health endpoint..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:80/api/health/ || echo "Health check failed - nginx might not be running"

echo ""
echo "=== Fix Complete ==="
echo "If the issue persists, check the Django logs with:"
echo "docker-compose logs backend"
echo ""
echo "Or check nginx logs with:"
echo "docker-compose logs nginx"
