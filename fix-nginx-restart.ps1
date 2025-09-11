# Fix Nginx Restart Loop and Configure SSL
# This script diagnoses and fixes nginx configuration issues

param(
    [switch]$ForceRebuild,
    [switch]$SkipSSL
)

Write-Host "🔧 Fixing Nginx Restart Loop and SSL Configuration" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Step 1: Generate self-signed certificates for fallback
Write-Host "📜 Step 1: Generating self-signed certificates..." -ForegroundColor Yellow
try {
    & ".\generate-selfsigned-cert.ps1"
} catch {
    Write-Host "❌ Failed to generate self-signed certificates" -ForegroundColor Red
    exit 1
}

# Step 2: Validate nginx configuration
Write-Host ""
Write-Host "🔍 Step 2: Validating nginx configuration..." -ForegroundColor Yellow
try {
    & ".\validate-nginx-config.ps1"
} catch {
    Write-Host "❌ Nginx configuration validation failed" -ForegroundColor Red
    exit 1
}

# Step 3: Stop existing containers
Write-Host ""
Write-Host "🛑 Step 3: Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.production.yml down 2>$null

# Step 4: Start services without nginx first
Write-Host ""
Write-Host "🏗️ Step 4: Starting backend and frontend services..." -ForegroundColor Yellow
$buildFlag = if ($ForceRebuild) { "--build" } else { "" }
docker-compose -f docker-compose.production.yml up -d $buildFlag postgres redis backend frontend

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Step 5: SSL Certificate Setup
if (!$SkipSSL) {
    Write-Host ""
    Write-Host "🔐 Step 5: Setting up SSL certificates..." -ForegroundColor Yellow

    # Create SSL directories
    New-Item -ItemType Directory -Path ssl/certbot/conf,ssl/certbot/www -Force | Out-Null

    # Check if certificates already exist
    if (!(Test-Path "ssl/certbot/conf/live/solevaeg.com")) {
        Write-Host "📜 Obtaining SSL certificates from Let's Encrypt..." -ForegroundColor Yellow

        # Start nginx temporarily for certificate validation
        docker-compose -f docker-compose.production.yml up -d nginx

        # Wait for nginx
        Start-Sleep -Seconds 10

        # Obtain certificates
        $certbotCommand = @"
docker run --rm -v `"${PWD}/ssl/certbot/conf:/etc/letsencrypt`" -v `"${PWD}/ssl/certbot/www:/var/www/certbot`" certbot/certbot certonly --webroot --webroot-path=/var/www/certbot --email support@solevaeg.com --agree-tos --no-eff-email -d solevaeg.com -d www.solevaeg.com
"@

        try {
            Invoke-Expression $certbotCommand
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ SSL certificates obtained successfully!" -ForegroundColor Green
            } else {
                Write-Host "⚠️ SSL certificate generation failed - will use self-signed certificates" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "⚠️ SSL certificate generation failed - will use self-signed certificates" -ForegroundColor Yellow
        }

        # Stop nginx temporarily
        docker-compose -f docker-compose.production.yml stop nginx
    } else {
        Write-Host "✅ SSL certificates already exist" -ForegroundColor Green
    }
} else {
    Write-Host ""
    Write-Host "⏭️ Step 5: Skipping SSL certificate setup" -ForegroundColor Yellow
}

# Step 6: Start nginx
Write-Host ""
Write-Host "🌐 Step 6: Starting nginx..." -ForegroundColor Yellow
docker-compose -f docker-compose.production.yml up -d nginx

# Wait for nginx to start
Start-Sleep -Seconds 10

# Step 7: Verify nginx is running
Write-Host ""
Write-Host "✅ Step 7: Verifying nginx container status..." -ForegroundColor Yellow

$nginxStatus = docker-compose -f docker-compose.production.yml ps nginx
if ($nginxStatus -match "Up") {
    Write-Host "✅ Nginx container is running successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Nginx container failed to start" -ForegroundColor Red

    # Show nginx logs for debugging
    Write-Host ""
    Write-Host "📋 Nginx container logs:" -ForegroundColor Yellow
    docker-compose -f docker-compose.production.yml logs nginx

    exit 1
}

# Step 8: Test basic functionality
Write-Host ""
Write-Host "🧪 Step 8: Testing basic functionality..." -ForegroundColor Yellow

try {
    # Test HTTP health endpoint
    $response = Invoke-WebRequest -Uri "http://localhost/health" -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ HTTP health check passed" -ForegroundColor Green
    } else {
        Write-Host "⚠️ HTTP health check returned: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ HTTP health check failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

try {
    # Test HTTPS health endpoint
    $response = Invoke-WebRequest -Uri "https://localhost/health" -SkipCertificateCheck -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ HTTPS health check passed" -ForegroundColor Green
    } else {
        Write-Host "⚠️ HTTPS health check returned: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ HTTPS health check failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 9: Show service status
Write-Host ""
Write-Host "📊 Step 9: Service Status" -ForegroundColor Yellow
docker-compose -f docker-compose.production.yml ps

Write-Host ""
Write-Host "🎉 Nginx restart loop fix completed!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Update DNS A records to point solevaeg.com and www.solevaeg.com to your server IP" -ForegroundColor Cyan
Write-Host "2. Test the live site: https://solevaeg.com" -ForegroundColor Cyan
if (!$SkipSSL) {
    Write-Host "3. Verify SSL certificate: https://www.ssllabs.com/ssltest/analyze.html?d=solevaeg.com" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "🔗 Useful Commands:" -ForegroundColor Cyan
Write-Host "- View nginx logs: docker-compose -f docker-compose.production.yml logs -f nginx" -ForegroundColor Cyan
Write-Host "- Restart nginx: docker-compose -f docker-compose.production.yml restart nginx" -ForegroundColor Cyan
Write-Host "- Check status: docker-compose -f docker-compose.production.yml ps" -ForegroundColor Cyan
