# Test Nginx Deployment and SSL Configuration
# This script tests the nginx setup after deployment

param(
    [string]$Domain = "solevaeg.com",
    [switch]$SkipLiveTests
)

Write-Host "🧪 Testing Nginx Deployment for $Domain" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Test 1: Check container status
Write-Host "📊 Test 1: Checking container status..." -ForegroundColor Yellow
$nginxStatus = docker-compose -f docker-compose.production.yml ps nginx 2>$null

if ($nginxStatus -match "Up") {
    Write-Host "✅ Nginx container is running" -ForegroundColor Green
} else {
    Write-Host "❌ Nginx container is not running" -ForegroundColor Red

    # Show recent logs
    Write-Host ""
    Write-Host "📋 Recent nginx logs:" -ForegroundColor Yellow
    docker-compose -f docker-compose.production.yml logs --tail=20 nginx
    exit 1
}

# Test 2: Test local HTTP access
Write-Host ""
Write-Host "🌐 Test 2: Testing local HTTP access..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost" -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ HTTP access successful (Status: $($response.StatusCode))" -ForegroundColor Green
    } else {
        Write-Host "⚠️ HTTP returned status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ HTTP access failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Test local HTTPS access
Write-Host ""
Write-Host "🔒 Test 3: Testing local HTTPS access..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://localhost" -SkipCertificateCheck -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ HTTPS access successful (Status: $($response.StatusCode))" -ForegroundColor Green
    } else {
        Write-Host "⚠️ HTTPS returned status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ HTTPS access failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Test HTTP to HTTPS redirect
Write-Host ""
Write-Host "🔄 Test 4: Testing HTTP to HTTPS redirect..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost" -MaximumRedirection 0 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 301) {
        $location = $response.Headers.Location
        if ($location -match "^https://") {
            Write-Host "✅ HTTP redirects to HTTPS: $location" -ForegroundColor Green
        } else {
            Write-Host "⚠️ HTTP redirects but not to HTTPS: $location" -ForegroundColor Yellow
        }
    } elseif ($response.StatusCode -eq 200) {
        Write-Host "⚠️ HTTP returns 200 directly (no redirect configured)" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️ HTTP returned status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ HTTP redirect test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Test API endpoint
Write-Host ""
Write-Host "🔌 Test 5: Testing API endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/" -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API endpoint accessible (Status: $($response.StatusCode))" -ForegroundColor Green
    } else {
        Write-Host "⚠️ API endpoint returned status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ API endpoint test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Test backend health
Write-Host ""
Write-Host "💓 Test 6: Testing backend health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/health/" -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend health check passed" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Backend health check returned: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 7: Live domain tests (if not skipped)
if (!$SkipLiveTests) {
    Write-Host ""
    Write-Host "🌍 Test 7: Testing live domain (if DNS is configured)..." -ForegroundColor Yellow

    try {
        $response = Invoke-WebRequest -Uri "http://$Domain" -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Live HTTP access successful for $Domain" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Live HTTP returned status: $($response.StatusCode) for $Domain" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ Live HTTP test failed for $Domain (DNS may not be configured)" -ForegroundColor Yellow
    }

    try {
        $response = Invoke-WebRequest -Uri "https://$Domain" -SkipCertificateCheck -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Live HTTPS access successful for $Domain" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Live HTTPS returned status: $($response.StatusCode) for $Domain" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ Live HTTPS test failed for $Domain (DNS or SSL may not be configured)" -ForegroundColor Yellow
    }
}

# Test 8: SSL Certificate check
Write-Host ""
Write-Host "🔐 Test 8: Checking SSL certificates..." -ForegroundColor Yellow

$letsEncryptPath = "ssl/certbot/conf/live/$Domain"
$selfSignedPath = "ssl/selfsigned"

if (Test-Path $letsEncryptPath) {
    Write-Host "✅ Let's Encrypt certificates found" -ForegroundColor Green
    $files = Get-ChildItem $letsEncryptPath
    foreach ($file in $files) {
        Write-Host "   - $($file.Name)" -ForegroundColor Green
    }
} elseif (Test-Path $selfSignedPath) {
    Write-Host "⚠️ Using self-signed certificates (Let's Encrypt not configured)" -ForegroundColor Yellow
    $files = Get-ChildItem $selfSignedPath
    foreach ($file in $files) {
        Write-Host "   - $($file.Name)" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ No SSL certificates found" -ForegroundColor Red
}

Write-Host ""
Write-Host "✨ Testing completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "- Nginx container should be running without restart loops" -ForegroundColor Cyan
Write-Host "- HTTP traffic should redirect to HTTPS" -ForegroundColor Cyan
Write-Host "- Frontend should serve static files correctly" -ForegroundColor Cyan
Write-Host "- API endpoints should proxy to backend" -ForegroundColor Cyan
Write-Host "- SSL certificates should be properly configured" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔗 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Configure DNS A records for $Domain and www.$Domain" -ForegroundColor Cyan
Write-Host "2. Test live domain: https://$Domain" -ForegroundColor Cyan
Write-Host "3. Verify SSL certificate validity" -ForegroundColor Cyan
