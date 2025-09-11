# SSL Certificate Initialization Script for Soleva (PowerShell)
# This script initializes SSL certificates using Let's Encrypt Certbot

param(
    [string]$Domain = "",
    [string]$Email = ""
)

# Load environment variables from docker.env
if (Test-Path "../docker.env") {
    Get-Content "../docker.env" | Where-Object { $_ -notmatch '^#' -and $_.Trim() -ne "" } | ForEach-Object {
        $key, $value = $_.Split('=', 2)
        Set-Variable -Name $key -Value $value -Scope Script
    }
}

# Check domain parameter or environment variable
if ($Domain -eq "" -and $script:DOMAIN -eq $null) {
    Write-Host "Error: Domain not specified. Use -Domain parameter or set DOMAIN in docker.env" -ForegroundColor Red
    exit 1
} elseif ($Domain -eq "") {
    $Domain = $script:DOMAIN
}

# Check email parameter or environment variable
if ($Email -eq "" -and $script:SSL_EMAIL -eq $null) {
    Write-Host "Error: Email not specified. Use -Email parameter or set SSL_EMAIL in docker.env" -ForegroundColor Red
    exit 1
} elseif ($Email -eq "") {
    $Email = $script:SSL_EMAIL
}

Write-Host "Initializing SSL certificates for $Domain and www.$Domain" -ForegroundColor Green
Write-Host "Using email: $Email" -ForegroundColor Green

# Stop nginx container temporarily
Write-Host "Stopping nginx container..." -ForegroundColor Yellow
docker stop soleva_nginx 2>$null

# Create certbot configuration directory if it doesn't exist
if (!(Test-Path "certbot")) {
    New-Item -ItemType Directory -Path "certbot" -Force
}

# Run certbot to get certificates
Write-Host "Requesting SSL certificates from Let's Encrypt..." -ForegroundColor Yellow

$certbotCommand = @"
docker run --rm -v "${PWD}/certbot/conf:/etc/letsencrypt" -v "${PWD}/certbot/www:/var/www/certbot" certbot/certbot certonly --webroot --webroot-path=/var/www/certbot --email $Email --agree-tos --no-eff-email -d $Domain -d www.$Domain
"@

Invoke-Expression $certbotCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "SSL certificates obtained successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to obtain SSL certificates" -ForegroundColor Red
    exit 1
}

# Generate DH parameters if not exists
$dhParamPath = "certbot/conf/ssl-dhparams.pem"
if (!(Test-Path $dhParamPath)) {
    Write-Host "Generating DH parameters..." -ForegroundColor Yellow
    openssl dhparam -out $dhParamPath 2048
}

# Start nginx again
Write-Host "Starting nginx container..." -ForegroundColor Yellow
docker start soleva_nginx

Write-Host ""
Write-Host "SSL certificates initialized successfully!" -ForegroundColor Green
Write-Host "Certificate files are located in: ssl/certbot/conf/live/$Domain/" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Update your DNS to point $Domain and www.$Domain to your server IP" -ForegroundColor Cyan
Write-Host "2. Wait for DNS propagation (can take up to 48 hours)" -ForegroundColor Cyan
Write-Host "3. Test HTTPS access: https://$Domain" -ForegroundColor Cyan
Write-Host "4. Certificates will auto-renew every 12 hours" -ForegroundColor Cyan
