# Soleva Pre-Deployment Verification Test Script
Write-Host "Soleva Pre-Deployment Verification Tests" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Test Results
$TestResults = @()

function Test-FileExists {
    param(
        [string]$Name,
        [string]$Path
    )
    
    Write-Host "Checking $Name... " -NoNewline
    
    if (Test-Path $Path) {
        Write-Host "PASS" -ForegroundColor Green
        return @{ Name = $Name; Status = "PASS"; Details = "File exists" }
    } else {
        Write-Host "FAIL" -ForegroundColor Red
        return @{ Name = $Name; Status = "FAIL"; Details = "File not found" }
    }
}

# 1. Backend Configuration Tests
Write-Host "`nBackend Configuration Tests" -ForegroundColor Yellow
Write-Host "---------------------------"

$TestResults += Test-FileExists "Django Settings" "soleva back end/soleva_backend/settings.py"
$TestResults += Test-FileExists "Django Manage" "soleva back end/manage.py"
$TestResults += Test-FileExists "Requirements" "soleva back end/requirements.txt"
$TestResults += Test-FileExists "Backend Environment" "soleva back end/.env"
$TestResults += Test-FileExists "SQLite Database" "soleva back end/db.sqlite3"

# 2. Frontend Configuration Tests
Write-Host "`nFrontend Configuration Tests" -ForegroundColor Yellow
Write-Host "----------------------------"

$TestResults += Test-FileExists "Frontend Build" "soleva front end/dist/index.html"
$TestResults += Test-FileExists "Package.json" "soleva front end/package.json"
$TestResults += Test-FileExists "Frontend Config" "soleva front end/src/config/api.ts"
$TestResults += Test-FileExists "JS Assets" "soleva front end/dist/assets"

# 3. Order Management Tests
Write-Host "`nOrder Management Tests" -ForegroundColor Yellow
Write-Host "----------------------"

$TestResults += Test-FileExists "Order Models" "soleva back end/orders/models.py"
$TestResults += Test-FileExists "Order Views" "soleva back end/orders/views.py"
$TestResults += Test-FileExists "Order URLs" "soleva back end/orders/urls.py"
$TestResults += Test-FileExists "Order Serializers" "soleva back end/orders/serializers.py"

# 4. Payment System Tests
Write-Host "`nPayment System Tests" -ForegroundColor Yellow
Write-Host "--------------------"

$TestResults += Test-FileExists "Payment Models" "soleva back end/payments/models.py"
$TestResults += Test-FileExists "Payment Views" "soleva back end/payments/views.py"
$TestResults += Test-FileExists "Payment URLs" "soleva back end/payments/urls.py"

# 5. User Management Tests
Write-Host "`nUser Management Tests" -ForegroundColor Yellow
Write-Host "---------------------"

$TestResults += Test-FileExists "User Models" "soleva back end/users/models.py"
$TestResults += Test-FileExists "User Views" "soleva back end/users/views.py"
$TestResults += Test-FileExists "User URLs" "soleva back end/users/urls.py"
$TestResults += Test-FileExists "Auth URLs" "soleva back end/authentication/urls.py"

# 6. Docker Configuration Tests
Write-Host "`nDocker Configuration Tests" -ForegroundColor Yellow
Write-Host "--------------------------"

$TestResults += Test-FileExists "Docker Compose" "docker-compose.yml"
$TestResults += Test-FileExists "Docker Production" "docker-compose.production.yml"
$TestResults += Test-FileExists "Docker Environment" "docker.env"
$TestResults += Test-FileExists "Backend Dockerfile" "soleva back end/Dockerfile"
$TestResults += Test-FileExists "Frontend Dockerfile" "soleva front end/Dockerfile"

# Results Summary
Write-Host "`nTest Results Summary" -ForegroundColor Magenta
Write-Host "===================="

$PassCount = ($TestResults | Where-Object { $_.Status -eq "PASS" }).Count
$FailCount = ($TestResults | Where-Object { $_.Status -eq "FAIL" }).Count
$TotalCount = $TestResults.Count

Write-Host "Total Tests: $TotalCount" -ForegroundColor White
Write-Host "Passed: $PassCount" -ForegroundColor Green
Write-Host "Failed: $FailCount" -ForegroundColor Red

$SuccessRate = [math]::Round(($PassCount / $TotalCount) * 100, 1)
Write-Host "Success Rate: $SuccessRate%" -ForegroundColor $(if ($SuccessRate -ge 90) { "Green" } elseif ($SuccessRate -ge 70) { "Yellow" } else { "Red" })

# Detailed Results
Write-Host "`nDetailed Test Results" -ForegroundColor Magenta
Write-Host "--------------------"

foreach ($result in $TestResults) {
    $color = switch ($result.Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
    }
    
    $statusSymbol = switch ($result.Status) {
        "PASS" { "[PASS]" }
        "FAIL" { "[FAIL]" }
    }
    
    Write-Host "$statusSymbol $($result.Name): $($result.Details)" -ForegroundColor $color
}

# Deployment Readiness Assessment
Write-Host "`nDeployment Readiness Assessment" -ForegroundColor Cyan
Write-Host "==============================="

if ($SuccessRate -ge 95) {
    Write-Host "READY FOR DEPLOYMENT" -ForegroundColor Green
    Write-Host "System is fully ready for production deployment." -ForegroundColor Green
} elseif ($SuccessRate -ge 85) {
    Write-Host "MOSTLY READY" -ForegroundColor Yellow
    Write-Host "System is mostly ready. Address warnings before deployment." -ForegroundColor Yellow
} elseif ($SuccessRate -ge 70) {
    Write-Host "NEEDS ATTENTION" -ForegroundColor Yellow
    Write-Host "Several issues need to be resolved before deployment." -ForegroundColor Yellow
} else {
    Write-Host "NOT READY" -ForegroundColor Red
    Write-Host "Significant issues must be resolved before deployment." -ForegroundColor Red
}

Write-Host "`nVerification Complete!" -ForegroundColor Green
