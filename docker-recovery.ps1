# Docker Recovery Script for Soleva
# Fixes common Docker issues and starts fresh

Write-Host "🔧 Soleva Docker Recovery Script" -ForegroundColor Yellow
Write-Host "This script will clean and restart your Docker environment" -ForegroundColor Cyan
Write-Host ""

# Check Docker Desktop status
Write-Host "🔍 Checking Docker Desktop status..." -ForegroundColor Blue
try {
    $dockerVersion = docker version --format "{{.Server.Version}}" 2>$null
    if ($dockerVersion) {
        Write-Host "✅ Docker Desktop is running (Version: $dockerVersion)" -ForegroundColor Green
    } else {
        throw "Docker not responding"
    }
} catch {
    Write-Host "❌ Docker Desktop is not running properly!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "  1. Close Docker Desktop completely" -ForegroundColor White
    Write-Host "  2. Restart Docker Desktop as Administrator" -ForegroundColor White
    Write-Host "  3. Wait for it to fully initialize (green status)" -ForegroundColor White
    Write-Host "  4. Run this script again" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Stop any running containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Blue
docker-compose down --volumes --remove-orphans 2>$null | Out-Null

# Clean Docker environment
Write-Host "🧹 Cleaning Docker environment..." -ForegroundColor Blue
Write-Host "   - Removing unused containers, networks, images..." -ForegroundColor Gray
docker system prune -a -f --volumes 2>$null | Out-Null

Write-Host "   - Removing custom networks..." -ForegroundColor Gray
docker network prune -f 2>$null | Out-Null

Write-Host "✅ Docker environment cleaned" -ForegroundColor Green

# Verify .env file exists
Write-Host "📝 Checking configuration..." -ForegroundColor Blue
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file missing! Creating from template..." -ForegroundColor Yellow
    Copy-Item "docker.env.example" -Destination ".env"
    Write-Host "✅ Created .env file" -ForegroundColor Green
    Write-Host "📋 Please edit .env with your actual values before production use" -ForegroundColor Cyan
} else {
    Write-Host "✅ .env file found" -ForegroundColor Green
}

# Start fresh
Write-Host "🚀 Starting Soleva with fresh containers..." -ForegroundColor Blue
Write-Host "   This may take a few minutes for first-time setup..." -ForegroundColor Gray

try {
    # Use --force-recreate to ensure fresh containers
    docker-compose up -d --build --force-recreate

    # Wait for services to initialize
    Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Blue
    Start-Sleep -Seconds 15

    # Check service status
    Write-Host "📊 Checking service status..." -ForegroundColor Blue
    $services = docker-compose ps --format "table {{.Service}}\t{{.State}}\t{{.Ports}}"
    Write-Host $services -ForegroundColor White

    Write-Host ""
    Write-Host "🎉 Docker Recovery Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Run migrations: docker-compose exec backend python manage.py migrate" -ForegroundColor White
    Write-Host "   2. Create admin user: docker-compose exec backend python manage.py createsuperuser" -ForegroundColor White
    Write-Host "   3. Visit: http://localhost" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 If services are not 'Up', check logs with:" -ForegroundColor Yellow
    Write-Host "   docker-compose logs [service-name]" -ForegroundColor White

} catch {
    Write-Host ""
    Write-Host "❌ Error during startup!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔍 Troubleshooting steps:" -ForegroundColor Yellow
    Write-Host "   1. Check Docker Desktop is running properly" -ForegroundColor White
    Write-Host "   2. Try running: docker-compose logs" -ForegroundColor White
    Write-Host "   3. Check DOCKER_TROUBLESHOOTING.md for more help" -ForegroundColor White
}

Write-Host ""
Read-Host "Press Enter to continue"
