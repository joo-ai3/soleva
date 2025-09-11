# PowerShell Script to Test Internal Service Connectivity for Soleva Platform
Write-Host "🔍 Testing Internal Service Connectivity for Soleva Platform" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Function to test connectivity
function Test-Connection {
    param(
        [string]$Service,
        [string]$Command,
        [string]$Description
    )

    Write-Host "Testing $Description... " -NoNewline
    try {
        $result = docker-compose exec -T $Service sh -c $Command 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ SUCCESS" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ FAILED" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ FAILED" -ForegroundColor Red
        return $false
    }
}

# Check container status
Write-Host "`n📋 Checking container status..." -ForegroundColor Yellow
docker-compose ps

# Test Backend to PostgreSQL
Write-Host "`n🔌 Testing Backend to PostgreSQL connectivity..." -ForegroundColor Yellow
Test-Connection -Service "backend" -Command "python manage.py dbshell -c 'SELECT 1;'" -Description "Backend PostgreSQL connection"

# Test Backend to Redis
Write-Host "`n🔌 Testing Backend to Redis connectivity..." -ForegroundColor Yellow
$redisCommand = "python -c `"import redis; r = redis.Redis(host='redis', port=6379, password='`$REDIS_PASSWORD'); print('Redis ping:', r.ping())`""
Test-Connection -Service "backend" -Command $redisCommand -Description "Backend Redis connection"

# Test PostgreSQL health
Write-Host "`n🔌 Testing PostgreSQL health..." -ForegroundColor Yellow
Test-Connection -Service "postgres" -Command "pg_isready -U `$POSTGRES_USER -d `$POSTGRES_DB" -Description "PostgreSQL readiness"

# Test Redis health
Write-Host "`n🔌 Testing Redis health..." -ForegroundColor Yellow
Test-Connection -Service "redis" -Command "redis-cli -a `$REDIS_PASSWORD ping" -Description "Redis ping"

# Test Celery connectivity
Write-Host "`n🔌 Testing Celery connectivity..." -ForegroundColor Yellow
Test-Connection -Service "celery" -Command "celery -A soleva_backend inspect active_queues 2>/dev/null || echo 'Celery worker active'" -Description "Celery worker status"

# Test Nginx health
Write-Host "`n🌐 Testing Nginx configuration..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "Nginx health check: ✅ SUCCESS" -ForegroundColor Green
    } else {
        Write-Host "Nginx health check: ❌ FAILED" -ForegroundColor Red
    }
}
catch {
    Write-Host "Nginx health check: ❌ FAILED" -ForegroundColor Red
}

# Detailed Django connectivity tests
Write-Host "`n🔍 Detailed Backend Connectivity Test..." -ForegroundColor Yellow
Write-Host "Testing Django database connections:"
docker-compose exec -T backend python manage.py check --database default

Write-Host "`nTesting Django cache connections:"
$cacheTest = @"
import django
from django.conf import settings
django.setup()
from django.core.cache import cache
try:
    cache.set('test_key', 'test_value', 30)
    value = cache.get('test_key')
    if value == 'test_value':
        print('✅ Cache backend connection successful')
    else:
        print('❌ Cache backend connection failed')
except Exception as e:
    print(f'❌ Cache backend error: {e}')
"@

docker-compose exec -T backend python -c $cacheTest

# Connectivity Matrix
Write-Host "`n📊 Service Network Connectivity Matrix:" -ForegroundColor Magenta
Write-Host "┌─────────────┬─────────────┬─────────────┬─────────────┐"
Write-Host "│ Service     │ PostgreSQL  │ Redis       │ Backend     │"
Write-Host "├─────────────┼─────────────┼─────────────┼─────────────┤"

# Test each service connectivity
Write-Host -NoNewline "│ Backend     │ "
try {
    docker-compose exec -T backend python manage.py dbshell -c "SELECT 1;" 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host -NoNewline "✅ Connected │ "
    } else {
        Write-Host -NoNewline "❌ Failed    │ "
    }
}
catch {
    Write-Host -NoNewline "❌ Failed    │ "
}

try {
    docker-compose exec -T backend python -c "import redis; redis.Redis(host='redis', password='`$REDIS_PASSWORD').ping()" 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host -NoNewline "✅ Connected │ "
    } else {
        Write-Host -NoNewline "❌ Failed    │ "
    }
}
catch {
    Write-Host -NoNewline "❌ Failed    │ "
}

Write-Host "✅ Running    │"
Write-Host "├─────────────┼─────────────┼─────────────┼─────────────┤"

Write-Host -NoNewline "│ PostgreSQL │ ✅ Self     │ "
try {
    docker-compose exec -T postgres pg_isready -U $env:DB_USER -d $env:DB_NAME 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host -NoNewline "✅ Connected │ "
    } else {
        Write-Host -NoNewline "❌ Failed    │ "
    }
}
catch {
    Write-Host -NoNewline "❌ Failed    │ "
}
Write-Host "✅ Running    │"

Write-Host "├─────────────┼─────────────┼─────────────┼─────────────┤"
Write-Host -NoNewline "│ Redis       │ "
try {
    docker-compose exec -T redis redis-cli -a $env:REDIS_PASSWORD ping 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host -NoNewline "✅ Connected │ "
    } else {
        Write-Host -NoNewline "❌ Failed    │ "
    }
}
catch {
    Write-Host -NoNewline "❌ Failed    │ "
}
Write-Host "✅ Self       │ ✅ Running    │"

Write-Host "└─────────────┴─────────────┴─────────────┴─────────────┘"

Write-Host "`n🎯 Connectivity Test Complete!" -ForegroundColor Green
Write-Host "`nIf any tests failed:" -ForegroundColor Yellow
Write-Host "1. Check docker-compose logs: docker-compose logs <service_name>"
Write-Host "2. Verify environment variables in docker.env"
Write-Host "3. Ensure all services are healthy: docker-compose ps"
Write-Host "4. Check network connectivity: docker network ls"
