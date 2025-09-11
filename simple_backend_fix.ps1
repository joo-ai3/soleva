# Simple backend fix script for Soleva
Write-Host "🔧 FIXING SOLEVA BACKEND CONTAINER ISSUES" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Stop all services
Write-Host "📋 Stopping all containers..." -ForegroundColor Yellow
docker compose down --remove-orphans

# Clean up
Write-Host "📋 Cleaning up old containers..." -ForegroundColor Yellow
docker system prune -f

# Rebuild from scratch
Write-Host "📋 Rebuilding containers..." -ForegroundColor Yellow
docker compose build --no-cache

# Start database first
Write-Host "📋 Starting database..." -ForegroundColor Yellow
docker compose up -d postgres redis

# Wait for database
Write-Host "📋 Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Start backend
Write-Host "📋 Starting backend..." -ForegroundColor Yellow
docker compose up -d backend

# Wait for backend
Start-Sleep -Seconds 10

# Check backend logs
Write-Host "📋 Checking backend logs..." -ForegroundColor Yellow
docker compose logs backend --tail=20

# Start remaining services
Write-Host "📋 Starting remaining services..." -ForegroundColor Yellow
docker compose up -d frontend nginx celery celery-beat

# Final status
Write-Host "📋 Service status:" -ForegroundColor Yellow
docker compose ps

Write-Host "" -ForegroundColor White
Write-Host "🎉 FIX COMPLETED!" -ForegroundColor Green
Write-Host "Check your website at: https://solevaeg.com" -ForegroundColor Cyan
