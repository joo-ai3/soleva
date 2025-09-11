# Test ALLOWED_HOSTS fix
Write-Host "🧪 Testing ALLOWED_HOSTS fix..." -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ Error: docker-compose.yml not found. Please run this from the project root." -ForegroundColor Red
    exit 1
}

# Check backend container status
Write-Host "Checking backend container status..." -ForegroundColor Cyan
docker compose ps backend

# Test the health endpoint from within the network (simulating nginx request)
Write-Host "Testing health endpoint from nginx container..." -ForegroundColor Cyan
docker compose exec nginx wget --no-verbose --tries=1 --spider http://backend:8000/api/health/

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Health endpoint accessible from nginx!" -ForegroundColor Green
} else {
    Write-Host "❌ Health endpoint not accessible from nginx" -ForegroundColor Red
    Write-Host "🔍 Checking backend logs for errors..." -ForegroundColor Yellow
    docker compose logs --tail=20 backend
}

# Show recent logs to see if DisallowedHost errors are gone
Write-Host "📋 Recent backend logs:" -ForegroundColor Cyan
docker compose logs --tail=10 backend | Select-String -Pattern "DisallowedHost|ALLOWED_HOSTS" -CaseSensitive:$false
