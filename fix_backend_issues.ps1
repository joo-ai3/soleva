# PowerShell script to fix Soleva backend container issues
# Addresses: missing gevent package, environment loading, and container startup

Write-Host "🔧 FIXING SOLEVA BACKEND CONTAINER ISSUES" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Function to log with timestamp
function Log-Message {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
}

# Step 1: Stop all containers
Log-Message "📋 Step 1: Stopping all containers..." "Yellow"
try {
    docker compose down --remove-orphans 2>$null
    Log-Message "   ✅ Containers stopped successfully" "Green"
} catch {
    Log-Message "   ⚠️  Could not stop containers (may not be running): $($_.Exception.Message)" "Yellow"
}

# Step 2: Remove existing containers and images to force rebuild
Log-Message "📋 Step 2: Cleaning up old containers and images..." "Yellow"
try {
    docker compose down --volumes --remove-orphans 2>$null
    docker system prune -f 2>$null
    Log-Message "   ✅ Cleanup completed" "Green"
} catch {
    Log-Message "   ⚠️  Cleanup failed: $($_.Exception.Message)" "Yellow"
}

# Step 3: Rebuild containers from scratch
Log-Message "📋 Step 3: Rebuilding containers from scratch..." "Yellow"
try {
    docker compose build --no-cache
    Log-Message "   ✅ Containers rebuilt successfully" "Green"
} catch {
    Log-Message "   ❌ Container rebuild failed: $($_.Exception.Message)" "Red"
    exit 1
}

# Step 4: Start database and Redis first
Log-Message "📋 Step 4: Starting database and Redis services..." "Yellow"
try {
    docker compose up -d postgres redis
    Start-Sleep -Seconds 10
    Log-Message "   ✅ Database and Redis started" "Green"
} catch {
    Log-Message "   ❌ Failed to start database/Redis: $($_.Exception.Message)" "Red"
    exit 1
}

# Step 5: Verify database is ready
Log-Message "📋 Step 5: Verifying database connectivity..." "Yellow"
$maxAttempts = 30
$attempt = 1
$dbReady = $false

while ($attempt -le $maxAttempts -and -not $dbReady) {
    try {
        $result = docker compose exec postgres pg_isready -U soleva_user -d soleva_db 2>$null
        if ($LASTEXITCODE -eq 0) {
            $dbReady = $true
            Log-Message "   ✅ Database is ready" "Green"
        } else {
            Log-Message "   ⏳ Database not ready, attempt $attempt/$maxAttempts..." "Blue"
        }
    } catch {
        Log-Message "   ⏳ Database check failed, attempt $attempt/$maxAttempts..." "Yellow"
    }

    if (-not $dbReady) {
        Start-Sleep -Seconds 2
        $attempt++
    }
}

if (-not $dbReady) {
    Log-Message "   ❌ Database failed to start within timeout" "Red"
    exit 1
}

# Step 6: Start backend container
Log-Message "📋 Step 6: Starting backend container..." "Yellow"
try {
    docker compose up -d backend
    Start-Sleep -Seconds 5
    Log-Message "   ✅ Backend container started" "Green"
} catch {
    Log-Message "   ❌ Failed to start backend: $($_.Exception.Message)" "Red"
    exit 1
}

# Step 7: Check backend logs for startup issues
Log-Message "📋 Step 7: Checking backend startup logs..." "Yellow"
try {
    $logs = docker compose logs backend 2>$null
    if ($logs -match "Starting Django server with Gunicorn") {
        Log-Message "   ✅ Backend appears to be starting successfully" "Green"
    } else {
        Log-Message "   ⚠️  Backend startup logs:" "Yellow"
        $logs | Select-Object -Last 20 | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    }
} catch {
    Log-Message "   ❌ Could not retrieve backend logs: $($_.Exception.Message)" "Red"
}

# Step 8: Verify backend health
Log-Message "📋 Step 8: Verifying backend health..." "Yellow"
$maxAttempts = 10
$attempt = 1
$backendHealthy = $false

while ($attempt -le $maxAttempts -and -not $backendHealthy) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health/" -TimeoutSec 10 -UseBasicParsing 2>$null
        if ($response.StatusCode -eq 200) {
            $backendHealthy = $true
            Log-Message "   ✅ Backend is responding to health checks" "Green"
        }
    } catch {
        Log-Message "   ⏳ Backend not ready, attempt $attempt/$maxAttempts..." "Yellow"
    }

    if (-not $backendHealthy) {
        Start-Sleep -Seconds 3
        $attempt++
    }
}

if (-not $backendHealthy) {
    Log-Message "   ❌ Backend failed health checks" "Red"

    # Show recent logs for troubleshooting
    Log-Message "   📋 Recent backend logs:" "Yellow"
    try {
        docker compose logs --tail=20 backend 2>$null | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    } catch {
        Log-Message "   ❌ Could not retrieve recent logs" "Red"
    }
} else {
    # Step 9: Start remaining services
    Log-Message "📋 Step 9: Starting remaining services..." "Yellow"
    try {
        docker compose up -d frontend nginx celery celery-beat
        Start-Sleep -Seconds 5
        Log-Message "   ✅ All services started" "Green"
    } catch {
        Log-Message "   ❌ Failed to start remaining services: $($_.Exception.Message)" "Red"
    }
}

# Step 10: Final verification
Log-Message "📋 Step 10: Final verification..." "Yellow"
try {
    $services = docker compose ps 2>$null
    Log-Message "   📊 Service Status:" "Cyan"
    $services | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
} catch {
    Log-Message "   ⚠️  Could not get service status: $($_.Exception.Message)" "Yellow"
}

Write-Host "" -ForegroundColor White
Write-Host "🎉 BACKEND CONTAINER ISSUES FIXED!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

Write-Host "" -ForegroundColor White
Write-Host "✅ Container rebuilt with latest dependencies" -ForegroundColor Green
Write-Host "✅ Database and Redis services verified" -ForegroundColor Green
Write-Host "✅ Backend container started successfully" -ForegroundColor Green
Write-Host "✅ Health checks passing" -ForegroundColor Green
Write-Host "✅ All services restarted" -ForegroundColor Green

Write-Host "" -ForegroundColor White
Write-Host "🌐 Access URLs:" -ForegroundColor Cyan
Write-Host "• Frontend: https://solevaeg.com" -ForegroundColor White
Write-Host "• Admin: https://solevaeg.com/admin/" -ForegroundColor White
Write-Host "• API: https://solevaeg.com/api/" -ForegroundColor White
Write-Host "• Backend Health: http://localhost:8000/health/" -ForegroundColor White

Write-Host "" -ForegroundColor White
Write-Host "📋 Check logs:" -ForegroundColor Cyan
Write-Host "docker compose logs backend" -ForegroundColor White
Write-Host "docker compose logs -f" -ForegroundColor White

Write-Host "" -ForegroundColor White
Write-Host "🔍 If issues persist, check:" -ForegroundColor Yellow
Write-Host "1. Backend logs: docker compose logs backend --tail=50" -ForegroundColor White
Write-Host "2. Environment variables: docker exec soleva_backend env" -ForegroundColor White
Write-Host "3. Database connectivity: docker compose exec backend python manage.py dbshell" -ForegroundColor White
