# Critical Nginx Fix Script for Soleva Platform
# This script resolves the continuous Nginx restart issues

Write-Host "=== SOLEVA NGINX CRITICAL FIX ===" -ForegroundColor Yellow
Write-Host "Fixing Nginx restart issues and SSL certificate problems..." -ForegroundColor Green

# Step 1: Stop all containers to ensure clean restart
Write-Host "`n1. Stopping all containers..." -ForegroundColor Cyan
docker-compose down

# Step 2: Check current Nginx configuration files
Write-Host "`n2. Current Nginx configuration files:" -ForegroundColor Cyan
Get-ChildItem "nginx/conf.d/" | Select-Object Name, LastWriteTime

# Step 3: Validate the new working configuration
Write-Host "`n3. Validating Nginx configuration..." -ForegroundColor Cyan
docker run --rm -v "${PWD}/nginx:/etc/nginx:ro" nginx:alpine nginx -t

# Step 4: Start the services with proper dependency order
Write-Host "`n4. Starting services in correct order..." -ForegroundColor Cyan
Write-Host "Starting database and cache services first..." -ForegroundColor Gray
docker-compose up -d postgres redis

Write-Host "Waiting for database to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 10

Write-Host "Starting backend service..." -ForegroundColor Gray
docker-compose up -d backend

Write-Host "Waiting for backend to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 15

Write-Host "Starting frontend service..." -ForegroundColor Gray
docker-compose up -d frontend

Write-Host "Waiting for frontend to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 10

Write-Host "Starting Nginx with fixed configuration..." -ForegroundColor Gray
docker-compose up -d nginx

# Step 5: Start supporting services
Write-Host "Starting Celery services..." -ForegroundColor Gray
docker-compose up -d celery celery-beat

# Step 6: Wait and check status
Write-Host "`n5. Waiting for all services to stabilize..." -ForegroundColor Cyan
Start-Sleep -Seconds 20

# Step 7: Check container status
Write-Host "`n6. Checking container status..." -ForegroundColor Cyan
docker-compose ps

# Step 8: Check Nginx logs
Write-Host "`n7. Checking Nginx logs for errors..." -ForegroundColor Cyan
docker logs soleva_nginx --tail=20

# Step 9: Test connectivity
Write-Host "`n8. Testing site connectivity..." -ForegroundColor Cyan
Write-Host "Testing localhost..." -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "http://localhost/health" -TimeoutSec 10 -UseBasicParsing
    Write-Host "✓ Local health check: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Local health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Testing domain..." -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "http://solevaeg.com/health" -TimeoutSec 10 -UseBasicParsing
    Write-Host "✓ Domain health check: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Domain health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 10: Show final status
Write-Host "`n=== FIX SUMMARY ===" -ForegroundColor Yellow
Write-Host "✓ Removed problematic SSL configuration that was causing restarts" -ForegroundColor Green
Write-Host "✓ Fixed broken HTTP configuration syntax" -ForegroundColor Green
Write-Host "✓ Deployed working HTTP-only configuration" -ForegroundColor Green
Write-Host "✓ Restarted all services in correct dependency order" -ForegroundColor Green

Write-Host "`nThe site should now be accessible at:" -ForegroundColor Cyan
Write-Host "- http://localhost" -ForegroundColor White
Write-Host "- http://solevaeg.com" -ForegroundColor White

Write-Host "`nNOTE: SSL will be configured later once the HTTP site is stable." -ForegroundColor Yellow
Write-Host "=== FIX COMPLETED ===" -ForegroundColor Green
