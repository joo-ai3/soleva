# Simple Soleva Startup Script
# Fixed version to start all services and check status

Write-Host "🚀 Starting Soleva Services" -ForegroundColor Green
Write-Host "===========================" -ForegroundColor Green

# Check Docker
Write-Host "📋 Checking Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Start services in order
Write-Host "🚀 Starting services..." -ForegroundColor Yellow

Write-Host "  📊 Starting database services..." -ForegroundColor Cyan
docker-compose up -d postgres redis

Write-Host "  ⏳ Waiting for database services..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host "  🔧 Starting backend..." -ForegroundColor Cyan
docker-compose up -d backend

Write-Host "  ⏳ Waiting for backend..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

Write-Host "  🎨 Starting frontend..." -ForegroundColor Cyan
docker-compose up -d frontend

Write-Host "  ⏳ Waiting for frontend..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host "  🌐 Starting nginx..." -ForegroundColor Cyan
docker-compose up -d nginx

Write-Host "  ⏳ Final startup wait..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Check status
Write-Host "🔍 Checking service status..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "📊 Service Health Check:" -ForegroundColor Yellow

$services = @("postgres", "redis", "backend", "frontend", "nginx")
foreach ($service in $services) {
    $container = docker ps -q -f name="soleva_$service"
    if ($container) {
        Write-Host "✅ $service is running" -ForegroundColor Green
    } else {
        Write-Host "❌ $service is not running" -ForegroundColor Red
        Write-Host "  📋 Checking logs for $service..." -ForegroundColor Yellow
        docker-compose logs --tail=5 $service
    }
}

Write-Host ""
Write-Host "🌐 Testing connectivity..." -ForegroundColor Yellow

# Test local connectivity
try {
    $response = Invoke-WebRequest -Uri "http://localhost/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Local health check: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Local health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Check if domain is set in env
if (Test-Path "docker.env") {
    $envContent = Get-Content "docker.env"
    $domainLine = $envContent | Where-Object { $_ -match "^DOMAIN=" }
    if ($domainLine) {
        $domain = $domainLine -replace "^DOMAIN=", ""
        Write-Host "🌐 Configured domain: $domain" -ForegroundColor Cyan
        
        try {
            $response = Invoke-WebRequest -Uri "http://$domain/health" -TimeoutSec 10 -UseBasicParsing
            Write-Host "✅ Domain health check: OK" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Domain not accessible yet: $($_.Exception.Message)" -ForegroundColor Yellow
            Write-Host "   This is normal if DNS is not configured yet." -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "📋 Access Information:" -ForegroundColor Cyan
Write-Host "   Local:     http://localhost" -ForegroundColor White
Write-Host "   Health:    http://localhost/health" -ForegroundColor White
Write-Host "   API:       http://localhost/api/" -ForegroundColor White
Write-Host "   Admin:     http://localhost/admin/" -ForegroundColor White

Write-Host ""
Write-Host "✅ Startup completed!" -ForegroundColor Green
Write-Host "💡 Use 'docker-compose logs [service]' to check individual service logs" -ForegroundColor Gray
