# Soleva Production Deployment Script with SSL Setup (PowerShell)
# This script deploys the application and sets up SSL certificates

param(
    [switch]$SkipSSL,
    [switch]$ForceRebuild
)

Write-Host "🚀 Starting Soleva Production Deployment with SSL Setup" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green

# Load environment variables from docker.env
if (Test-Path "docker.env") {
    Get-Content "docker.env" | Where-Object { $_ -notmatch '^#' -and $_.Trim() -ne "" } | ForEach-Object {
        $key, $value = $_.Split('=', 2)
        Set-Variable -Name $key -Value $value -Scope Script
    }
}

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed. Please install Docker first." -ForegroundColor Red
    exit 1
}

if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor Red
    exit 1
}

# Check if domain is configured
if ($script:DOMAIN -eq $null) {
    Write-Host "❌ DOMAIN environment variable is not set" -ForegroundColor Red
    Write-Host "Please set DOMAIN=solevaeg.com in docker.env file" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Prerequisites check passed" -ForegroundColor Green

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path ssl/certbot/conf,ssl/certbot/www,logs/nginx -Force | Out-Null

# Stop existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.production.yml down 2>$null

# Build and start services (except certbot initially)
Write-Host "🏗️ Building and starting services..." -ForegroundColor Yellow
$buildFlag = if ($ForceRebuild) { "--build" } else { "" }
docker-compose -f docker-compose.production.yml up -d $buildFlag postgres redis backend frontend

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Initialize SSL certificates
if (!$SkipSSL) {
    Write-Host "🔐 Initializing SSL certificates..." -ForegroundColor Yellow

    if (!(Test-Path "ssl/certbot/conf/live/$($script:DOMAIN)")) {
        Write-Host "📜 Obtaining SSL certificates from Let's Encrypt..." -ForegroundColor Yellow

        $certbotCommand = @"
docker run --rm -v "${PWD}/ssl/certbot/conf:/etc/letsencrypt" -v "${PWD}/ssl/certbot/www:/var/www/certbot" certbot/certbot certonly --webroot --webroot-path=/var/www/certbot --email $($script:SSL_EMAIL) --agree-tos --no-eff-email -d $($script:DOMAIN) -d www.$($script:DOMAIN)
"@

        Invoke-Expression $certbotCommand

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ SSL certificates obtained successfully!" -ForegroundColor Green

            # Generate DH parameters
            Write-Host "🔧 Generating DH parameters..." -ForegroundColor Yellow
            openssl dhparam -out ssl/certbot/conf/ssl-dhparams.pem 2048
        } else {
            Write-Host "❌ Failed to obtain SSL certificates" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "✅ SSL certificates already exist" -ForegroundColor Green
    }
} else {
    Write-Host "⏭️ Skipping SSL certificate setup" -ForegroundColor Yellow
}

# Start nginx and certbot
Write-Host "🌐 Starting nginx and certbot services..." -ForegroundColor Yellow
if (!$SkipSSL) {
    docker-compose -f docker-compose.production.yml up -d nginx certbot
} else {
    docker-compose -f docker-compose.production.yml up -d nginx
}

# Wait for nginx to start
Write-Host "⏳ Waiting for nginx to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test the deployment
Write-Host "🧪 Testing deployment..." -ForegroundColor Yellow

try {
    Write-Host "Testing HTTP to HTTPS redirect..." -ForegroundColor Yellow
    $response = Invoke-WebRequest -Uri "http://localhost" -MaximumRedirection 0 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 301) {
        Write-Host "✅ HTTP redirect working" -ForegroundColor Green
    } else {
        Write-Host "⚠️ HTTP redirect may not be working" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ HTTP redirect test failed (may be normal if nginx is not binding to localhost)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Update your DNS A records to point $($script:DOMAIN) and www.$($script:DOMAIN) to your server IP" -ForegroundColor Cyan
Write-Host "2. Wait for DNS propagation (can take up to 48 hours)" -ForegroundColor Cyan
Write-Host "3. Test the live site: https://$($script:DOMAIN)" -ForegroundColor Cyan
if (!$SkipSSL) {
    Write-Host "4. Monitor SSL certificate renewal (happens automatically every 12 hours)" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "🔗 Useful commands:" -ForegroundColor Cyan
Write-Host "- View logs: docker-compose -f docker-compose.production.yml logs -f" -ForegroundColor Cyan
Write-Host "- Restart services: docker-compose -f docker-compose.production.yml restart" -ForegroundColor Cyan
if (!$SkipSSL) {
    Write-Host "- Renew SSL manually: .\ssl\renew-ssl.ps1" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Cyan
docker-compose -f docker-compose.production.yml ps
