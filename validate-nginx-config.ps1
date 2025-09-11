# Nginx Configuration Validation Script
# This script validates the nginx configuration before deployment

Write-Host "🔍 Validating Nginx Configuration..." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Create a temporary nginx container to test configuration
Write-Host "Testing nginx configuration syntax..." -ForegroundColor Yellow

$nginxConfig = @"
nginx:alpine -t -c /etc/nginx/nginx.conf -p /tmp/nginx-test
"@

# Copy configuration files to a temporary location for testing
if (!(Test-Path "temp-nginx-test")) {
    New-Item -ItemType Directory -Path temp-nginx-test -Force | Out-Null
}

# Copy nginx configuration
Copy-Item nginx/nginx.conf temp-nginx-test/nginx.conf -Force
Copy-Item nginx/conf.d/*.conf temp-nginx-test/conf.d/ -Force -Recurse
Copy-Item nginx/ssl temp-nginx-test/ssl/ -Force -Recurse

Write-Host "✅ Configuration files copied for testing" -ForegroundColor Green

# Create a simple test container to validate config
Write-Host "Creating test container to validate configuration..." -ForegroundColor Yellow

$dockerCommand = @"
docker run --rm -v `"${PWD}/temp-nginx-test:/etc/nginx`" nginx:alpine nginx -t -c /etc/nginx/nginx.conf
"@

try {
    Invoke-Expression $dockerCommand
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Nginx configuration is valid!" -ForegroundColor Green
    } else {
        Write-Host "❌ Nginx configuration has errors" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Failed to validate nginx configuration: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Check for SSL certificates
Write-Host ""
Write-Host "🔐 Checking SSL Certificates..." -ForegroundColor Yellow

$sslPath = "ssl/certbot/conf/live/solevaeg.com"
if (Test-Path $sslPath) {
    Write-Host "✅ SSL certificates found at: $sslPath" -ForegroundColor Green

    $files = Get-ChildItem $sslPath
    foreach ($file in $files) {
        Write-Host "   - $($file.Name)" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️ SSL certificates not found. They will be obtained during first deployment." -ForegroundColor Yellow
    Write-Host "   Path: $sslPath" -ForegroundColor Yellow
}

# Check environment variables
Write-Host ""
Write-Host "🔧 Checking Environment Variables..." -ForegroundColor Yellow

if (Test-Path "docker.env") {
    $envContent = Get-Content "docker.env" | Where-Object { $_ -notmatch '^#' -and $_.Trim() -ne "" }
    $domainFound = $false
    $sslEmailFound = $false

    foreach ($line in $envContent) {
        if ($line -match "^DOMAIN=") {
            $domainFound = $true
            $domain = ($line -split '=', 2)[1]
            Write-Host "✅ DOMAIN: $domain" -ForegroundColor Green
        }
        if ($line -match "^SSL_EMAIL=") {
            $sslEmailFound = $true
            $sslEmail = ($line -split '=', 2)[1]
            Write-Host "✅ SSL_EMAIL: $sslEmail" -ForegroundColor Green
        }
    }

    if (!$domainFound) {
        Write-Host "❌ DOMAIN not found in docker.env" -ForegroundColor Red
    }
    if (!$sslEmailFound) {
        Write-Host "❌ SSL_EMAIL not found in docker.env" -ForegroundColor Red
    }
} else {
    Write-Host "❌ docker.env file not found" -ForegroundColor Red
}

# Clean up
Remove-Item temp-nginx-test -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✨ Configuration validation complete!" -ForegroundColor Green
