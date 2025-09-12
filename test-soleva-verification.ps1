# Soleva Pre-Deployment Verification Test Script
# This script tests all critical functionality for deployment readiness

Write-Host "🚀 Soleva Pre-Deployment Verification Tests" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Configuration
$BACKEND_URL = "http://localhost:8000"
$FRONTEND_URL = "http://localhost:5173"
$API_BASE = "$BACKEND_URL/api"

# Test Results
$TestResults = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Headers = @{},
        [string]$Body = $null
    )
    
    Write-Host "Testing $Name... " -NoNewline
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = $Headers
            UseBasicParsing = $true
            TimeoutSec = 10
        }
        
        if ($Body) {
            $params.Body = $Body
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @params
        
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ PASS" -ForegroundColor Green
            return @{ Name = $Name; Status = "PASS"; Details = "HTTP $($response.StatusCode)" }
        } else {
            Write-Host "⚠️ WARN" -ForegroundColor Yellow
            return @{ Name = $Name; Status = "WARN"; Details = "HTTP $($response.StatusCode)" }
        }
    }
    catch {
        Write-Host "❌ FAIL" -ForegroundColor Red
        return @{ Name = $Name; Status = "FAIL"; Details = $_.Exception.Message }
    }
}

function Test-FileExists {
    param(
        [string]$Name,
        [string]$Path
    )
    
    Write-Host "Checking $Name... " -NoNewline
    
    if (Test-Path $Path) {
        Write-Host "✅ PASS" -ForegroundColor Green
        return @{ Name = $Name; Status = "PASS"; Details = "File exists" }
    } else {
        Write-Host "❌ FAIL" -ForegroundColor Red
        return @{ Name = $Name; Status = "FAIL"; Details = "File not found" }
    }
}

# 1. Backend ↔ Frontend Communication Tests
Write-Host "`n🔗 Backend ↔ Frontend Communication Tests" -ForegroundColor Yellow
Write-Host "-" * 45

$TestResults += Test-Endpoint "Backend Health Check" "$API_BASE/health/"
$TestResults += Test-Endpoint "API Root" "$API_BASE/"
$TestResults += Test-Endpoint "Authentication Endpoints" "$API_BASE/auth/"
$TestResults += Test-Endpoint "Products API" "$API_BASE/products/"
$TestResults += Test-Endpoint "Orders API" "$API_BASE/orders/"
$TestResults += Test-Endpoint "Cart API" "$API_BASE/cart/"

# 2. Frontend Build and Assets Tests
Write-Host "`n📱 Frontend Build and Assets Tests" -ForegroundColor Yellow
Write-Host "-" * 35

$TestResults += Test-FileExists "Frontend Build" "soleva front end/dist/index.html"
$TestResults += Test-FileExists "CSS Assets" "soleva front end/dist/assets/styles"
$TestResults += Test-FileExists "JS Assets" "soleva front end/dist/assets"
$TestResults += Test-FileExists "Package.json" "soleva front end/package.json"

# 3. Order & Account Management Tests
Write-Host "`n👤 Order & Account Management Tests" -ForegroundColor Yellow
Write-Host "-" * 37

$TestResults += Test-Endpoint "User Registration Endpoint" "$API_BASE/auth/register/"
$TestResults += Test-Endpoint "User Login Endpoint" "$API_BASE/auth/login/"
$TestResults += Test-Endpoint "Order Creation Endpoint" "$API_BASE/orders/" "POST"
$TestResults += Test-Endpoint "Order Tracking" "$API_BASE/orders/track/"

# 4. Payment and Proof System Tests
Write-Host "`n💳 Payment and Proof System Tests" -ForegroundColor Yellow
Write-Host "-" * 32

$TestResults += Test-Endpoint "Payment Proofs API" "$API_BASE/orders/payment-proofs/"
$TestResults += Test-FileExists "Payment Proof Models" "soleva back end/orders/models.py"
$TestResults += Test-FileExists "Payment Proof Views" "soleva back end/orders/views.py"
$TestResults += Test-FileExists "Payment Proof Serializers" "soleva back end/orders/serializers.py"

# 5. Configuration and Environment Tests
Write-Host "`n⚙️ Configuration and Environment Tests" -ForegroundColor Yellow
Write-Host "-" * 37

$TestResults += Test-FileExists "Backend Environment" "soleva back end/.env"
$TestResults += Test-FileExists "Django Settings" "soleva back end/soleva_backend/settings.py"
$TestResults += Test-FileExists "Frontend Config" "soleva front end/src/config/api.ts"
$TestResults += Test-FileExists "Docker Compose" "docker-compose.yml"

# 6. Database and Migration Tests
Write-Host "`n🗄️ Database and Migration Tests" -ForegroundColor Yellow
Write-Host "-" * 30

$TestResults += Test-FileExists "SQLite Database" "soleva back end/db.sqlite3"
$TestResults += Test-FileExists "Requirements" "soleva back end/requirements.txt"
$TestResults += Test-FileExists "Django Manage" "soleva back end/manage.py"

# 7. Error Handling and Logging Tests
Write-Host "`n🛡️ Error Handling and Logging Tests" -ForegroundColor Yellow
Write-Host "-" * 34

$TestResults += Test-FileExists "Backend Logs Directory" "soleva back end/logs"
$TestResults += Test-FileExists "Error Handler Utils" "soleva back end/utils/exception_handler.py"
$TestResults += Test-FileExists "Frontend Error Components" "soleva front end/src/components/ErrorMessage.tsx"

# Results Summary
Write-Host "`n📊 Test Results Summary" -ForegroundColor Magenta
Write-Host "=" * 25

$PassCount = ($TestResults | Where-Object { $_.Status -eq "PASS" }).Count
$WarnCount = ($TestResults | Where-Object { $_.Status -eq "WARN" }).Count
$FailCount = ($TestResults | Where-Object { $_.Status -eq "FAIL" }).Count
$TotalCount = $TestResults.Count

Write-Host "Total Tests: $TotalCount" -ForegroundColor White
Write-Host "Passed: $PassCount" -ForegroundColor Green
Write-Host "Warnings: $WarnCount" -ForegroundColor Yellow
Write-Host "Failed: $FailCount" -ForegroundColor Red

$SuccessRate = [math]::Round(($PassCount / $TotalCount) * 100, 1)
Write-Host "Success Rate: $SuccessRate%" -ForegroundColor $(if ($SuccessRate -ge 90) { "Green" } elseif ($SuccessRate -ge 70) { "Yellow" } else { "Red" })

# Detailed Results
Write-Host "`n📋 Detailed Test Results" -ForegroundColor Magenta
Write-Host "-" * 25

foreach ($result in $TestResults) {
    $color = switch ($result.Status) {
        "PASS" { "Green" }
        "WARN" { "Yellow" }
        "FAIL" { "Red" }
    }
    
    $statusSymbol = switch ($result.Status) {
        "PASS" { "✅" }
        "WARN" { "⚠️" }
        "FAIL" { "❌" }
    }
    
    Write-Host "$statusSymbol $($result.Name): $($result.Details)" -ForegroundColor $color
}

# Deployment Readiness Assessment
Write-Host "`n🚀 Deployment Readiness Assessment" -ForegroundColor Cyan
Write-Host "=" * 35

if ($SuccessRate -ge 95) {
    Write-Host "✅ READY FOR DEPLOYMENT" -ForegroundColor Green
    Write-Host "System is fully ready for production deployment." -ForegroundColor Green
} elseif ($SuccessRate -ge 85) {
    Write-Host "⚠️ MOSTLY READY" -ForegroundColor Yellow
    Write-Host "System is mostly ready. Address warnings before deployment." -ForegroundColor Yellow
} elseif ($SuccessRate -ge 70) {
    Write-Host "⚠️ NEEDS ATTENTION" -ForegroundColor Yellow
    Write-Host "Several issues need to be resolved before deployment." -ForegroundColor Yellow
} else {
    Write-Host "❌ NOT READY" -ForegroundColor Red
    Write-Host "Significant issues must be resolved before deployment." -ForegroundColor Red
}

# Next Steps
Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Start backend server: cd 'soleva back end'; python manage.py runserver"
Write-Host "2. Start frontend server: cd 'soleva front end'; npm run dev"
Write-Host "3. Re-run this script to test live endpoints"
Write-Host "4. Review failed tests and resolve issues"
Write-Host "5. Deploy to production environment"

Write-Host "`nVerification Complete!" -ForegroundColor Green
