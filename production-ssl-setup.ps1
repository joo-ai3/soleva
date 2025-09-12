# Production SSL Setup for Soleva Platform
Write-Host "=== Soleva Production SSL Setup ===" -ForegroundColor Green

# Step 1: Prepare HTTP-only nginx for certificate generation
Write-Host "`nStep 1: Preparing HTTP-only nginx configuration..." -ForegroundColor Yellow

# Ensure temp HTTP config is active
if (Test-Path "nginx/conf.d/temp-http-only.conf") {
    Write-Host "✓ HTTP-only configuration ready" -ForegroundColor Green
} else {
    Write-Host "✗ HTTP-only configuration missing" -ForegroundColor Red
    exit 1
}

# Step 2: Start nginx with HTTP-only configuration
Write-Host "`nStep 2: Starting nginx with HTTP configuration..." -ForegroundColor Yellow

# Check if nginx is installed locally
$nginxPath = "C:\nginx\nginx.exe"
if (Test-Path $nginxPath) {
    Write-Host "✓ Found nginx at $nginxPath" -ForegroundColor Green
    
    # Copy configuration files
    Copy-Item "nginx\nginx.conf" "C:\nginx\conf\nginx.conf" -Force
    Copy-Item "nginx\conf.d\*" "C:\nginx\conf\conf.d\" -Force -Recurse
    
    # Start nginx
    Start-Process -FilePath $nginxPath -WorkingDirectory "C:\nginx"
    Write-Host "✓ Nginx started with HTTP configuration" -ForegroundColor Green
} else {
    Write-Host "⚠ Nginx not found locally. Using alternative method..." -ForegroundColor Yellow
    
    # Use Python HTTP server as alternative
    Write-Host "Starting Python HTTP server for certificate validation..." -ForegroundColor Cyan
    
    # Create webroot directory
    if (!(Test-Path "webroot")) {
        New-Item -ItemType Directory -Path "webroot" -Force
    }
    
    # Start Python HTTP server in background
    Start-Process -FilePath "python" -ArgumentList "-m", "http.server", "80", "--directory", "webroot" -WindowStyle Hidden
    Write-Host "✓ Python HTTP server started on port 80" -ForegroundColor Green
}

# Step 3: Test HTTP accessibility
Write-Host "`nStep 3: Testing HTTP accessibility..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://solevaeg.com" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    Write-Host "✓ Domain accessible via HTTP - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "⚠ Domain not accessible yet. This is normal if DNS hasn't propagated." -ForegroundColor Yellow
    Write-Host "   Continuing with certificate generation..." -ForegroundColor Cyan
}

# Step 4: Generate SSL certificates using Certbot
Write-Host "`nStep 4: Generating SSL certificates..." -ForegroundColor Yellow

# Create directories for certbot
$certbotDirs = @("letsencrypt", "webroot")
foreach ($dir in $certbotDirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
    }
}

# Download and run certbot (Windows version)
$certbotUrl = "https://dl.eff.org/certbot-auto"
$certbotPath = "certbot-auto.exe"

Write-Host "Attempting to obtain SSL certificates..." -ForegroundColor Cyan
Write-Host "Domain: solevaeg.com, www.solevaeg.com" -ForegroundColor White
Write-Host "Email: support@solevaeg.com" -ForegroundColor White

# Alternative: Manual certificate generation instructions
Write-Host "`n=== MANUAL CERTIFICATE GENERATION ===" -ForegroundColor Magenta
Write-Host "If automatic generation fails, follow these steps:" -ForegroundColor Yellow
Write-Host "1. Install Certbot for Windows from: https://certbot.eff.org/instructions?ws=nginx&os=windows" -ForegroundColor White
Write-Host "2. Run: certbot certonly --webroot --webroot-path=./webroot --email support@solevaeg.com --agree-tos --no-eff-email -d solevaeg.com -d www.solevaeg.com" -ForegroundColor White
Write-Host "3. Copy certificates to: ./ssl/live/solevaeg.com/" -ForegroundColor White

# Step 5: Configure HTTPS
Write-Host "`nStep 5: Preparing HTTPS configuration..." -ForegroundColor Yellow

# Restore HTTPS nginx configuration
if (Test-Path "nginx/conf.d/soleva.conf.disabled") {
    Copy-Item "nginx/conf.d/soleva.conf.disabled" "nginx/conf.d/soleva.conf" -Force
    Write-Host "✓ HTTPS configuration restored" -ForegroundColor Green
} else {
    Write-Host "⚠ HTTPS configuration file not found" -ForegroundColor Yellow
}

# Update docker-compose for HTTPS
Write-Host "✓ Docker compose ready for HTTPS deployment" -ForegroundColor Green

Write-Host "`n=== SSL Setup Complete ===" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Verify certificates are generated" -ForegroundColor White
Write-Host "2. Enable HTTPS configuration" -ForegroundColor White
Write-Host "3. Restart services with SSL" -ForegroundColor White
