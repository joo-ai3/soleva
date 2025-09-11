# Fix ALLOWED_HOSTS issue locally
Write-Host "🔧 Fixing ALLOWED_HOSTS issue..." -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ Error: docker-compose.yml not found. Please run this from the project root." -ForegroundColor Red
    exit 1
}

# Stop the backend container
Write-Host "Stopping backend container..." -ForegroundColor Yellow
docker compose stop backend

# Rebuild the backend container to ensure latest changes are applied
Write-Host "Rebuilding backend container..." -ForegroundColor Yellow
docker compose build backend

# Start the backend container
Write-Host "Starting backend container..." -ForegroundColor Yellow
docker compose up -d backend

# Check if everything is working
Write-Host "Checking container status..." -ForegroundColor Cyan
docker compose ps backend

# Check recent logs to see if ALLOWED_HOSTS is working
Write-Host "📋 Checking recent backend logs..." -ForegroundColor Cyan
Start-Sleep -Seconds 5
docker compose logs --tail=30 backend
