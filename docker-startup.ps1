# Soleva Docker Startup Script
# This script sets up and starts the Soleva application using Docker

Write-Host "🚀 Starting Soleva Docker Environment..." -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found! Creating from template..." -ForegroundColor Red
    Copy-Item "docker.env.example" -Destination ".env"
    Write-Host "✅ Created .env file. Please update it with your actual values." -ForegroundColor Yellow
    Write-Host "📝 Edit .env file with your database passwords, API keys, etc." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ .env file found" -ForegroundColor Green

# Check Docker is running
Write-Host "🔍 Checking Docker status..." -ForegroundColor Blue
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Clean up any existing containers (optional)
Write-Host "🧹 Cleaning up existing containers..." -ForegroundColor Blue
docker-compose down --remove-orphans 2>$null

# Pull latest images
Write-Host "📦 Pulling Docker images..." -ForegroundColor Blue
docker-compose pull

# Build and start services
Write-Host "🏗️  Building and starting services..." -ForegroundColor Blue
docker-compose up -d --build

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Blue
Start-Sleep -Seconds 10

# Check service status
Write-Host "📊 Checking service status..." -ForegroundColor Blue
docker-compose ps

Write-Host ""
Write-Host "🎉 Soleva Docker Environment Started!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Service URLs:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost" -ForegroundColor White
Write-Host "   Backend API: http://localhost/api" -ForegroundColor White
Write-Host "   Admin Panel: http://localhost/admin" -ForegroundColor White
Write-Host "   Database: localhost:5432" -ForegroundColor White
Write-Host "   Redis: localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Run migrations: docker-compose exec backend python manage.py migrate" -ForegroundColor White
Write-Host "   2. Create superuser: docker-compose exec backend python manage.py createsuperuser" -ForegroundColor White
Write-Host "   3. Collect static files: docker-compose exec backend python manage.py collectstatic --noinput" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Useful Commands:" -ForegroundColor Cyan
Write-Host "   View logs: docker-compose logs -f [service-name]" -ForegroundColor White
Write-Host "   Stop services: docker-compose down" -ForegroundColor White
Write-Host "   Restart service: docker-compose restart [service-name]" -ForegroundColor White
