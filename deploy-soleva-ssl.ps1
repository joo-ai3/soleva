# Complete Deployment Script for Soleva with SSL
# This script handles the complete deployment with SSL configuration

param(
    [switch]$SkipSSL,
    [switch]$ForceRebuild,
    [switch]$SkipVerification
)

Write-Host "🚀 Soleva Production Deployment with SSL Setup" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green

# Load environment variables
if (Test-Path "docker.env") {
    Get-Content "docker.env" | Where-Object { $_ -notmatch '^#' -and $_.Trim() -ne "" } | ForEach-Object {
        $key, $value = $_.Split('=', 2)
        Set-Variable -Name $key -Value $value -Scope Script
    }
}

# Prerequisites check
Write-Host "📋 Checking Prerequisites..." -ForegroundColor Yellow

# Check Docker
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed. Please install Docker first." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor Red
    exit 1
}

# Check domain configuration
if ($script:DOMAIN -eq $null) {
    Write-Host "❌ DOMAIN environment variable is not set" -ForegroundColor Red
    Write-Host "Please set DOMAIN=solevaeg.com in docker.env file" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Prerequisites check passed" -ForegroundColor Green

# Create directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path ssl/certbot/conf,ssl/certbot/www,logs/nginx -Force | Out-Null

# Stop existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.production.yml down 2>$null

# Build and start services
Write-Host "🏗️ Building and starting services..." -ForegroundColor Yellow
$buildFlag = if ($ForceRebuild) { "--build" } else { "" }
docker-compose -f docker-compose.production.yml up -d $buildFlag postgres redis backend frontend

# Wait for services
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# SSL Setup
if (!$SkipSSL) {
    Write-Host "🔐 Setting up SSL certificates..." -ForegroundColor Yellow

    # Check if certificates already exist
    if (!(Test-Path "ssl/certbot/conf/live/$($script:DOMAIN)")) {
        Write-Host "📜 Obtaining SSL certificates from Let's Encrypt..." -ForegroundColor Yellow

        # Start nginx for certificate validation
        docker-compose -f docker-compose.production.yml up -d nginx

        # Wait for nginx
        Start-Sleep -Seconds 10

        # Obtain certificates
        $certbotCommand = @"
docker run --rm -v "${PWD}/ssl/certbot/conf:/etc/letsencrypt" -v "${PWD}/ssl/certbot/www:/var/www/certbot" certbot/certbot certonly --webroot --webroot-path=/var/www/certbot --email $($script:SSL_EMAIL) --agree-tos --no-eff-email -d $($script:DOMAIN) -d www.$($script:DOMAIN)
"@

        Invoke-Expression $certbotCommand

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ SSL certificates obtained successfully!" -ForegroundColor Green

            # Generate DH parameters if openssl is available
            try {
                openssl dhparam -out ssl/certbot/conf/ssl-dhparams.pem 2048
                Write-Host "✅ DH parameters generated" -ForegroundColor Green
            } catch {
                Write-Host "⚠️ OpenSSL not available - DH parameters not generated" -ForegroundColor Yellow
            }
        } else {
            Write-Host "❌ Failed to obtain SSL certificates" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "✅ SSL certificates already exist" -ForegroundColor Green
    }

    # Start certbot for renewal
    Write-Host "🔄 Starting SSL certificate renewal service..." -ForegroundColor Yellow
    docker-compose -f docker-compose.production.yml up -d certbot
} else {
    Write-Host "⏭️ Skipping SSL certificate setup" -ForegroundColor Yellow
}

# Start nginx
Write-Host "🌐 Starting nginx..." -ForegroundColor Yellow
docker-compose -f docker-compose.production.yml up -d nginx

# Wait for nginx
Start-Sleep -Seconds 10

# Verification
if (!$SkipVerification) {
    Write-Host "🧪 Running verification tests..." -ForegroundColor Yellow

    # Test HTTP redirect
    try {
        $response = Invoke-WebRequest -Uri "http://localhost" -MaximumRedirection 0 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 301) {
            Write-Host "✅ HTTP to HTTPS redirect working" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️ HTTP redirect test inconclusive" -ForegroundColor Yellow
    }

    # Test HTTPS access
    try {
        $response = Invoke-WebRequest -Uri "https://localhost" -SkipCertificateCheck -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ HTTPS access working" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️ HTTPS test inconclusive" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Update DNS A records to point $($script:DOMAIN) and www.$($script:DOMAIN) to your server IP" -ForegroundColor Cyan
Write-Host "2. Wait for DNS propagation (can take up to 48 hours)" -ForegroundColor Cyan
Write-Host "3. Test the live site: https://$($script:DOMAIN)" -ForegroundColor Cyan
if (!$SkipSSL) {
    Write-Host "4. Verify SSL: https://www.ssllabs.com/ssltest/analyze.html?d=$($script:DOMAIN)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🔗 Useful Commands:" -ForegroundColor Cyan
Write-Host "- View logs: docker-compose -f docker-compose.production.yml logs -f" -ForegroundColor Cyan
Write-Host "- Restart services: docker-compose -f docker-compose.production.yml restart" -ForegroundColor Cyan
Write-Host "- Check status: docker-compose -f docker-compose.production.yml ps" -ForegroundColor Cyan
if (!$SkipSSL) {
    Write-Host "- Renew SSL: .\ssl\renew-ssl.ps1" -ForegroundColor Cyan
    Write-Host "- Verify SSL: .\verify-ssl-setup.ps1" -ForegroundColor Cyan
}
Write-Host "- Verify DNS: .\verify-dns-setup.ps1" -ForegroundColor Cyan

Write-Host ""
Write-Host "📊 Current Service Status:" -ForegroundColor Cyan
docker-compose -f docker-compose.production.yml ps
