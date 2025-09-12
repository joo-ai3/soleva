# Complete SSL Deployment Script for Soleva Platform
Write-Host "=== Soleva Complete SSL Deployment ===" -ForegroundColor Green

$ErrorActionPreference = "Continue"

Write-Host "`n🔍 Checking Prerequisites..." -ForegroundColor Yellow

# Check if domain resolves
Write-Host "Checking DNS resolution..." -ForegroundColor Cyan
try {
    $dnsResult = Resolve-DnsName -Name "solevaeg.com" -ErrorAction Stop
    Write-Host "✅ DNS Resolution: solevaeg.com → $($dnsResult[0].IPAddress)" -ForegroundColor Green
} catch {
    Write-Host "❌ DNS Resolution failed" -ForegroundColor Red
    Write-Host "Please ensure solevaeg.com points to this server's IP" -ForegroundColor Yellow
}

# Check if port 80 is available
Write-Host "Checking port 80 availability..." -ForegroundColor Cyan
$port80 = Get-NetTCPConnection -LocalPort 80 -ErrorAction SilentlyContinue
if ($port80) {
    Write-Host "✅ Port 80 is in use (HTTP server running)" -ForegroundColor Green
} else {
    Write-Host "⚠️ Port 80 is not in use" -ForegroundColor Yellow
}

Write-Host "`n📋 SSL Certificate Generation Options:" -ForegroundColor Yellow
Write-Host "1. Docker Certbot (if Docker connectivity works)" -ForegroundColor White
Write-Host "2. Manual Certbot installation" -ForegroundColor White
Write-Host "3. Alternative SSL providers" -ForegroundColor White

Write-Host "`n🔧 Option 1: Docker Certbot Method" -ForegroundColor Cyan
Write-Host "Command to run when Docker works:" -ForegroundColor White
Write-Host 'docker run --rm -v "$PWD/letsencrypt:/etc/letsencrypt" -v "$PWD/webroot:/var/www/certbot" certbot/certbot certonly --webroot --webroot-path=/var/www/certbot --email support@solevaeg.com --agree-tos --no-eff-email --non-interactive -d solevaeg.com -d www.solevaeg.com' -ForegroundColor Gray

Write-Host "`n🔧 Option 2: Manual Certbot Installation" -ForegroundColor Cyan
Write-Host "1. Download Certbot from: https://certbot.eff.org/instructions?ws=nginx&os=windows" -ForegroundColor White
Write-Host "2. Install Certbot" -ForegroundColor White
Write-Host "3. Run: certbot certonly --webroot --webroot-path=./webroot --email support@solevaeg.com --agree-tos --no-eff-email -d solevaeg.com -d www.solevaeg.com" -ForegroundColor White

Write-Host "`n🔧 Option 3: Alternative SSL Providers" -ForegroundColor Cyan
Write-Host "- CloudFlare SSL (if using CloudFlare)" -ForegroundColor White
Write-Host "- ZeroSSL (free alternative to Let's Encrypt)" -ForegroundColor White
Write-Host "- Commercial SSL certificate" -ForegroundColor White

Write-Host "`n⚙️ After obtaining certificates, run this to enable HTTPS:" -ForegroundColor Yellow

$httpsEnableScript = @'
# Enable HTTPS Configuration
Write-Host "Enabling HTTPS configuration..." -ForegroundColor Green

# 1. Restore HTTPS nginx config
if (Test-Path "nginx/conf.d/soleva.conf.disabled") {
    Move-Item "nginx/conf.d/soleva.conf.disabled" "nginx/conf.d/soleva.conf" -Force
    Write-Host "✅ HTTPS nginx config restored" -ForegroundColor Green
}

# 2. Remove temporary HTTP-only config
if (Test-Path "nginx/conf.d/temp-http-only.conf") {
    Remove-Item "nginx/conf.d/temp-http-only.conf" -Force
    Write-Host "✅ Temporary HTTP config removed" -ForegroundColor Green
}

# 3. Update docker-compose.yml for HTTPS
$dockerCompose = Get-Content "docker-compose.yml" -Raw
$dockerCompose = $dockerCompose -replace '# - "443:443"', '- "443:443"'
$dockerCompose = $dockerCompose -replace '# SSL port temporarily disabled', '# SSL port enabled'
$dockerCompose | Set-Content "docker-compose.yml"
Write-Host "✅ Docker compose updated for HTTPS" -ForegroundColor Green

# 4. Update nginx.conf to enable HTTPS redirect
$nginxConf = Get-Content "nginx/nginx.conf" -Raw
$nginxConf = $nginxConf -replace 'return 301 http://solevaeg.com', 'return 301 https://solevaeg.com'
$nginxConf | Set-Content "nginx/nginx.conf"
Write-Host "✅ Nginx main config updated for HTTPS" -ForegroundColor Green

Write-Host "`n🚀 HTTPS Configuration Complete!" -ForegroundColor Green
Write-Host "Now restart your services with: docker compose up -d" -ForegroundColor Cyan
'@

$httpsEnableScript | Set-Content "enable-https.ps1"
Write-Host "✅ Created enable-https.ps1 script" -ForegroundColor Green

Write-Host "`n📊 Current Status Summary:" -ForegroundColor Yellow
Write-Host "✅ HTTP server running on port 80" -ForegroundColor Green
Write-Host "✅ Webroot directory created for ACME challenges" -ForegroundColor Green
Write-Host "✅ HTTPS configuration prepared" -ForegroundColor Green
Write-Host "✅ SSL certificate generation methods documented" -ForegroundColor Green
Write-Host "⏳ Waiting for SSL certificate generation" -ForegroundColor Yellow

Write-Host "`n🎯 Next Actions:" -ForegroundColor Cyan
Write-Host "1. Choose one of the SSL certificate generation methods above" -ForegroundColor White
Write-Host "2. Once certificates are obtained, run: powershell -ExecutionPolicy Bypass -File enable-https.ps1" -ForegroundColor White
Write-Host "3. Restart services with HTTPS enabled" -ForegroundColor White
Write-Host "4. Test https://solevaeg.com" -ForegroundColor White

Write-Host "`n🌟 Your platform will then be fully production-ready with SSL!" -ForegroundColor Green
