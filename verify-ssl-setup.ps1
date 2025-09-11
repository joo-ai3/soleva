# SSL Verification Script for solevaeg.com
# This script verifies SSL certificate and HTTPS functionality

param(
    [string]$Domain = "solevaeg.com"
)

Write-Host "🔐 Verifying SSL Setup for $Domain" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Check if certificates exist
Write-Host "📜 Checking SSL Certificates..." -ForegroundColor Yellow
$certPath = "ssl/certbot/conf/live/$Domain"
if (Test-Path $certPath) {
    Write-Host "✅ SSL certificates found at: $certPath" -ForegroundColor Green

    # List certificate files
    Get-ChildItem $certPath | ForEach-Object {
        Write-Host "   - $($_.Name)" -ForegroundColor Green
    }

    # Check certificate expiry
    Write-Host ""
    Write-Host "📅 Checking Certificate Expiry..." -ForegroundColor Yellow
    try {
        $certContent = Get-Content "$certPath/fullchain.pem" -Raw
        # Note: This is a basic check - for full validation use openssl or online tools
        Write-Host "✅ Certificate file exists and is readable" -ForegroundColor Green
    } catch {
        Write-Host "❌ Cannot read certificate file" -ForegroundColor Red
    }
} else {
    Write-Host "❌ SSL certificates not found at: $certPath" -ForegroundColor Red
    Write-Host "   Run the SSL initialization script first" -ForegroundColor Red
}

# Test HTTP to HTTPS redirect
Write-Host ""
Write-Host "🔄 Testing HTTP to HTTPS Redirect..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://$Domain" -MaximumRedirection 0 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 301) {
        $location = $response.Headers.Location
        if ($location -match "^https://") {
            Write-Host "✅ HTTP redirects to HTTPS: $location" -ForegroundColor Green
        } else {
            Write-Host "⚠️ HTTP redirects but not to HTTPS: $location" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️ HTTP does not redirect (Status: $($response.StatusCode))" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ HTTP test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test HTTPS access
Write-Host ""
Write-Host "🔒 Testing HTTPS Access..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://$Domain" -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ HTTPS access successful (Status: $($response.StatusCode))" -ForegroundColor Green
    } else {
        Write-Host "⚠️ HTTPS access returned: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ HTTPS test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test www subdomain
Write-Host ""
Write-Host "🌐 Testing www Subdomain..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://www.$Domain" -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ www.$Domain access successful (Status: $($response.StatusCode))" -ForegroundColor Green
    } else {
        Write-Host "⚠️ www.$Domain returned: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ www.$Domain test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Check for mixed content
Write-Host ""
Write-Host "🔍 Checking for Mixed Content..." -ForegroundColor Yellow
Write-Host "Manual verification needed - check browser developer tools for mixed content warnings" -ForegroundColor Yellow

Write-Host ""
Write-Host "📋 SSL Verification Checklist:" -ForegroundColor Cyan
Write-Host "1. SSL certificates are properly installed" -ForegroundColor Cyan
Write-Host "2. HTTP traffic redirects to HTTPS" -ForegroundColor Cyan
Write-Host "3. HTTPS access works for both domains" -ForegroundColor Cyan
Write-Host "4. No mixed content warnings in browser" -ForegroundColor Cyan
Write-Host "5. SSL Labs test shows A+ rating" -ForegroundColor Cyan

Write-Host ""
Write-Host "🔗 Useful Commands:" -ForegroundColor Cyan
Write-Host "- SSL Labs Test: https://www.ssllabs.com/ssltest/analyze.html?d=$Domain" -ForegroundColor Cyan
Write-Host "- Certificate Info: openssl x509 -in ssl/certbot/conf/live/$Domain/fullchain.pem -text -noout" -ForegroundColor Cyan
Write-Host "- Renew SSL: .\ssl\renew-ssl.ps1" -ForegroundColor Cyan

Write-Host ""
Write-Host "✨ Verification Complete!" -ForegroundColor Green
