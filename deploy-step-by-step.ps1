# Soleva Step-by-Step Deployment Script
# This script handles the SSL certificate chicken-and-egg problem

Write-Host "=== Soleva Step-by-Step Deployment ===" -ForegroundColor Green

# Step 1: Stop any running containers
Write-Host "Step 1: Stopping existing containers..." -ForegroundColor Yellow
docker compose down --remove-orphans

# Step 2: Clean up any conflicting containers
Write-Host "Step 2: Cleaning up..." -ForegroundColor Yellow
docker container prune -f

# Step 3: Create initial HTTP-only deployment
Write-Host "Step 3: Starting HTTP-only deployment..." -ForegroundColor Yellow
docker compose -f docker-compose.initial.yml up -d

# Step 4: Wait for services to be ready
Write-Host "Step 4: Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Step 5: Check if services are running
Write-Host "Step 5: Checking service status..." -ForegroundColor Yellow
docker compose -f docker-compose.initial.yml ps

# Step 6: Test HTTP connectivity
Write-Host "Step 6: Testing HTTP connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://solevaeg.com" -TimeoutSec 10 -UseBasicParsing
    Write-Host "HTTP connection successful! Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "HTTP connection failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "This is expected if DNS is not pointing to this server yet." -ForegroundColor Yellow
}

# Step 7: Get SSL certificates (only if HTTP is working)
Write-Host "Step 7: Obtaining SSL certificates..." -ForegroundColor Yellow
Write-Host "Running Certbot to get SSL certificates..." -ForegroundColor Cyan

# Run certbot manually
docker run --rm -v "soleva_letsencrypt_certs:/etc/letsencrypt" -v "soleva_certbot_webroot:/var/www/certbot" certbot/certbot certonly --webroot --webroot-path=/var/www/certbot --email "support@solevaeg.com" --agree-tos --no-eff-email --non-interactive --keep-until-expiring -d "solevaeg.com" -d "www.solevaeg.com"

if ($LASTEXITCODE -eq 0) {
    Write-Host "SSL certificates obtained successfully!" -ForegroundColor Green
    
    # Step 8: Re-enable HTTPS configuration
    Write-Host "Step 8: Enabling HTTPS configuration..." -ForegroundColor Yellow
    
    # Restore the original nginx configuration
    if (Test-Path "nginx/conf.d/soleva.conf.disabled") {
        Move-Item "nginx/conf.d/soleva.conf.disabled" "nginx/conf.d/soleva.conf" -Force
        Write-Host "Restored HTTPS configuration" -ForegroundColor Green
    }
    
    # Step 9: Switch to full HTTPS deployment
    Write-Host "Step 9: Switching to HTTPS deployment..." -ForegroundColor Yellow
    docker compose down
    docker compose up -d
    
    Write-Host "=== Deployment Complete! ===" -ForegroundColor Green
    Write-Host "Your site should now be available at https://solevaeg.com" -ForegroundColor Cyan
    
} else {
    Write-Host "SSL certificate generation failed. The site will remain HTTP-only." -ForegroundColor Red
    Write-Host "Please check that:" -ForegroundColor Yellow
    Write-Host "1. DNS is pointing solevaeg.com to this server (213.130.147.41)" -ForegroundColor Yellow
    Write-Host "2. Port 80 is open and accessible from the internet" -ForegroundColor Yellow
    Write-Host "3. No firewall is blocking HTTP traffic" -ForegroundColor Yellow
    
    Write-Host "The site is available at http://solevaeg.com for now." -ForegroundColor Cyan
}

Write-Host "=== Script Complete ===" -ForegroundColor Green
