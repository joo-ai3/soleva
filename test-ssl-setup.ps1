# SSL Setup Test Script for Soleva (PowerShell)
# This script tests the SSL certificate installation and HTTPS configuration

# Load environment variables from docker.env
if (Test-Path "docker.env") {
    Get-Content "docker.env" | Where-Object { $_ -notmatch '^#' -and $_.Trim() -ne "" } | ForEach-Object {
        $key, $value = $_.Split('=', 2)
        Set-Variable -Name $key -Value $value -Scope Script
    }
}

# Colors for output
$RED = "`e[0;31m"
$GREEN = "`e[0;32m"
$YELLOW = "`e[1;33m"
$BLUE = "`e[0;34m"
$NC = "`e[0m" # No Color

Write-Host "$BLUE[SSL-TEST] SSL Setup Verification for Soleva$NC" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue

# Check if domain is configured
if ($script:DOMAIN -eq $null) {
    Write-Host "$RED[ERROR] DOMAIN environment variable is not set$NC" -ForegroundColor Red
    exit 1
}

Write-Host "$BLUE Domain:$NC $($script:DOMAIN)" -ForegroundColor Blue
Write-Host "$BLUE SSL Email:$NC $($script:SSL_EMAIL)" -ForegroundColor Blue
Write-Host ""

# Check SSL certificate files
Write-Host "$YELLOW[FILES] Checking SSL certificate files...$NC" -ForegroundColor Yellow

$CERT_PATH = "ssl/certbot/conf/live/$($script:DOMAIN)"
if (Test-Path $CERT_PATH) {
    Write-Host "$GREEN[SUCCESS] Certificate directory exists: $CERT_PATH$NC" -ForegroundColor Green

    if (Test-Path "$CERT_PATH/fullchain.pem") {
        Write-Host "$GREEN[SUCCESS] Full chain certificate found$NC" -ForegroundColor Green
    } else {
        Write-Host "$RED[ERROR] Full chain certificate missing$NC" -ForegroundColor Red
    }

    if (Test-Path "$CERT_PATH/privkey.pem") {
        Write-Host "$GREEN[SUCCESS] Private key found$NC" -ForegroundColor Green
    } else {
        Write-Host "$RED[ERROR] Private key missing$NC" -ForegroundColor Red
    }
} else {
    Write-Host "$RED[ERROR] Certificate directory not found: $CERT_PATH$NC" -ForegroundColor Red
    Write-Host "$YELLOW[INFO] Run .\ssl\init-ssl.ps1 to obtain certificates$NC" -ForegroundColor Yellow
}

# Check DH parameters
if (Test-Path "ssl/certbot/conf/ssl-dhparams.pem") {
    Write-Host "$GREEN[SUCCESS] DH parameters file exists$NC" -ForegroundColor Green
} else {
    Write-Host "$RED[ERROR] DH parameters file missing$NC" -ForegroundColor Red
}

Write-Host ""

# Check Docker services
Write-Host "$YELLOW[DOCKER] Checking Docker services...$NC" -ForegroundColor Yellow

$nginxRunning = docker ps | Select-String -Pattern "soleva_nginx"
if ($nginxRunning) {
    Write-Host "$GREEN[SUCCESS] Nginx container is running$NC" -ForegroundColor Green
} else {
    Write-Host "$RED[ERROR] Nginx container is not running$NC" -ForegroundColor Red
}

$certbotRunning = docker ps | Select-String -Pattern "soleva_certbot"
if ($certbotRunning) {
    Write-Host "$GREEN[SUCCESS] Certbot container is running$NC" -ForegroundColor Green
} else {
    Write-Host "$RED[ERROR] Certbot container is not running$NC" -ForegroundColor Red
}

Write-Host ""

# Test HTTP to HTTPS redirect (if nginx is running locally)
Write-Host "$YELLOW[REDIRECT] Testing HTTP to HTTPS redirect...$NC" -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost" -MaximumRedirection 0 -ErrorAction Stop
    if ($response.StatusCode -eq 301) {
        Write-Host "$GREEN[SUCCESS] HTTP redirect is working$NC" -ForegroundColor Green
    } else {
        Write-Host "$YELLOW[WARNING] HTTP redirect status: $($response.StatusCode)$NC" -ForegroundColor Yellow
    }
} catch {
    Write-Host "$YELLOW[WARNING] HTTP redirect test failed (may be normal if nginx is not binding to localhost)$NC" -ForegroundColor Yellow
}

# Test HTTPS access (if nginx is running locally)
try {
    $response = Invoke-WebRequest -Uri "https://localhost" -SkipCertificateCheck -MaximumRedirection 0 -ErrorAction Stop
    if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 301) {
        Write-Host "$GREEN[SUCCESS] HTTPS access is working$NC" -ForegroundColor Green
    } else {
        Write-Host "$YELLOW[WARNING] HTTPS access status: $($response.StatusCode)$NC" -ForegroundColor Yellow
    }
} catch {
    Write-Host "$YELLOW[WARNING] HTTPS access test failed (may be normal if nginx is not binding to localhost)$NC" -ForegroundColor Yellow
}

Write-Host ""

# DNS check (external)
Write-Host "$YELLOW[DNS] DNS Configuration Check...$NC" -ForegroundColor Yellow

try {
    $domainResult = Resolve-DnsName -Name $script:DOMAIN -Type A -ErrorAction Stop
    $wwwDomainResult = Resolve-DnsName -Name "www.$($script:DOMAIN)" -Type A -ErrorAction Stop

    if ($domainResult) {
        Write-Host "$GREEN[SUCCESS] $($script:DOMAIN) resolves to: $($domainResult.IPAddress)$NC" -ForegroundColor Green
    }

    if ($wwwDomainResult) {
        Write-Host "$GREEN[SUCCESS] www.$($script:DOMAIN) resolves to: $($wwwDomainResult.IPAddress)$NC" -ForegroundColor Green
    }

    # Check if IPs match
    if ($domainResult.IPAddress -eq $wwwDomainResult.IPAddress -and $domainResult.IPAddress -ne $null) {
        Write-Host "$GREEN[SUCCESS] DNS records match$NC" -ForegroundColor Green
    } elseif ($domainResult.IPAddress -ne $null -and $wwwDomainResult.IPAddress -ne $null) {
        Write-Host "$YELLOW[WARNING] DNS records don't match - this may cause issues$NC" -ForegroundColor Yellow
    }
} catch {
    Write-Host "$YELLOW[WARNING] DNS resolution failed - this may be normal if DNS hasn't propagated yet$NC" -ForegroundColor Yellow
}

Write-Host ""

# SSL Certificate validation (if certificates exist)
if (Test-Path "$CERT_PATH/fullchain.pem") {
    Write-Host "$YELLOW[SSL] SSL Certificate Information...$NC" -ForegroundColor Yellow

    # Get certificate info
    $certInfo = & openssl x509 -in "$CERT_PATH/fullchain.pem" -text -noout 2>$null

    # Extract expiry date
    $expiryLine = $certInfo | Select-String -Pattern "Not After"
    if ($expiryLine) {
        $expiryDate = $expiryLine.Line -replace ".*Not After : ", ""
        Write-Host "$BLUE Certificate expires:$NC $expiryDate" -ForegroundColor Blue
    }

    # Check if certificate is valid
    $certCheck = & openssl x509 -checkend 86400 -in "$CERT_PATH/fullchain.pem" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "$GREEN[SUCCESS] Certificate is valid (not expired)$NC" -ForegroundColor Green
    } else {
        Write-Host "$RED[ERROR] Certificate has expired or will expire within 24 hours$NC" -ForegroundColor Red
    }

    # Check domains in certificate
    $certDomains = ($certInfo | Select-String -Pattern "DNS:" | ForEach-Object { $_.Line -replace ".*DNS:", "" -replace "\s+", "" }) -join ", "
    Write-Host "$BLUE Certificate domains:$NC $certDomains" -ForegroundColor Blue

    if ($certDomains -match $script:DOMAIN) {
        Write-Host "$GREEN[SUCCESS] Primary domain ($($script:DOMAIN)) is in certificate$NC" -ForegroundColor Green
    } else {
        Write-Host "$RED[ERROR] Primary domain ($($script:DOMAIN)) is not in certificate$NC" -ForegroundColor Red
    }

    if ($certDomains -match "www.$($script:DOMAIN)") {
        Write-Host "$GREEN[SUCCESS] WWW domain (www.$($script:DOMAIN)) is in certificate$NC" -ForegroundColor Green
    } else {
        Write-Host "$RED[ERROR] WWW domain (www.$($script:DOMAIN)) is not in certificate$NC" -ForegroundColor Red
    }
}

Write-Host ""

# Recommendations
Write-Host "$BLUE[INFO] Recommendations:$NC" -ForegroundColor Blue
Write-Host "1. Ensure DNS A records point to your server IP:" -ForegroundColor Blue
Write-Host "   $($script:DOMAIN) A [YOUR_SERVER_IP]" -ForegroundColor Blue
Write-Host "   www.$($script:DOMAIN) A [YOUR_SERVER_IP]" -ForegroundColor Blue
Write-Host ""
Write-Host "2. Test live URLs after DNS propagation:" -ForegroundColor Blue
Write-Host "   https://$($script:DOMAIN)" -ForegroundColor Blue
Write-Host "   https://www.$($script:DOMAIN)" -ForegroundColor Blue
Write-Host "   http://$($script:DOMAIN) (should redirect to HTTPS)" -ForegroundColor Blue
Write-Host "   http://www.$($script:DOMAIN) (should redirect to HTTPS)" -ForegroundColor Blue
Write-Host ""
Write-Host "3. SSL certificates auto-renew every 12 hours via certbot container" -ForegroundColor Blue
Write-Host "4. Monitor logs: docker-compose -f docker-compose.production.yml logs -f nginx" -ForegroundColor Blue
Write-Host ""

Write-Host "$GREEN[SUCCESS] SSL setup verification completed!$NC" -ForegroundColor Green
