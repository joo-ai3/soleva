#!/usr/bin/env powershell
# Soleva Website Deployment Verification Script
# This script verifies all components are ready for VPS deployment

param(
    [switch]$Verbose,
    [switch]$SkipDocker,
    [string]$Domain = "solevaeg.com"
)

Write-Host "🚀 Soleva Website - Deployment Verification Script" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

$ErrorCount = 0
$WarningCount = 0

function Write-Check {
    param($Message, $Status = "INFO", $Details = "")
    $Color = switch ($Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "WARN" { "Yellow" }
        default { "White" }
    }
    
    $Icon = switch ($Status) {
        "PASS" { "[PASS]" }
        "FAIL" { "[FAIL]" }
        "WARN" { "[WARN]" }
        default { "[INFO]" }
    }
    
    Write-Host "$Icon $Message" -ForegroundColor $Color
    if ($Details -and $Verbose) {
        Write-Host "   $Details" -ForegroundColor Gray
    }
    
    if ($Status -eq "FAIL") { $script:ErrorCount++ }
    if ($Status -eq "WARN") { $script:WarningCount++ }
}

# 1. Check Project Structure
Write-Host "`n📁 Checking Project Structure..." -ForegroundColor Cyan

$RequiredFiles = @(
    "docker-compose.yml",
    "docker.env",
    "nginx/conf.d/soleva.conf",
    "soleva back end/Dockerfile",
    "soleva front end/Dockerfile",
    "soleva back end/requirements.txt",
    "soleva front end/package.json"
)

foreach ($file in $RequiredFiles) {
    if (Test-Path $file) {
        Write-Check "Found: $file" "PASS"
    } else {
        Write-Check "Missing: $file" "FAIL" "This file is required for deployment"
    }
}

# 2. Check Environment Configuration
Write-Host "`n⚙️ Checking Environment Configuration..." -ForegroundColor Cyan

if (Test-Path "docker.env") {
    $envContent = Get-Content "docker.env"
    
    # Check critical environment variables
    $criticalVars = @(
        "DOMAIN=solevaeg.com",
        "SSL_EMAIL=admin@solevaeg.com",
        "ADMIN_USERNAME=soleva_admin",
        "ADMIN_PASSWORD=?3aeeSjqq",
        "USE_SQLITE=False"
    )
    
    foreach ($var in $criticalVars) {
        if ($envContent -match [regex]::Escape($var)) {
            Write-Check "Environment variable configured: $($var.Split('=')[0])" "PASS"
        } else {
            Write-Check "Missing or incorrect: $($var.Split('=')[0])" "FAIL"
        }
    }
    
    # Check for placeholder values
    $placeholders = @("your-", "change-this", "example", "test")
    foreach ($placeholder in $placeholders) {
        if ($envContent -match $placeholder) {
            Write-Check "Found placeholder values in environment" "WARN" "Update production values"
        }
    }
} else {
    Write-Check "docker.env file missing" "FAIL"
}

# 3. Check Database Configuration
Write-Host "`n🗄️ Checking Database Configuration..." -ForegroundColor Cyan

$dbConfig = @{
    "PostgreSQL configured" = $envContent -match "DB_HOST=postgres"
    "Database name set" = $envContent -match "DB_NAME=soleva_db"
    "Database user set" = $envContent -match "DB_USER=soleva_user"
    "SQLite disabled" = $envContent -match "USE_SQLITE=False"
}

foreach ($check in $dbConfig.GetEnumerator()) {
    if ($check.Value) {
        Write-Check $check.Key "PASS"
    } else {
        Write-Check $check.Key "FAIL"
    }
}

# 4. Check Nginx Configuration
Write-Host "`n🌐 Checking Nginx Configuration..." -ForegroundColor Cyan

if (Test-Path "nginx/conf.d/soleva.conf") {
    $nginxConfig = Get-Content "nginx/conf.d/soleva.conf"
    
    $nginxChecks = @{
        "Domain configured for solevaeg.com" = $nginxConfig -match "solevaeg.com"
        "SSL configuration present" = $nginxConfig -match "ssl_certificate"
        "Backend proxy configured" = $nginxConfig -match "proxy_pass.*backend"
        "Frontend proxy configured" = $nginxConfig -match "proxy_pass.*frontend"
        "Security headers configured" = $nginxConfig -match "X-Frame-Options"
    }
    
    foreach ($check in $nginxChecks.GetEnumerator()) {
        if ($check.Value) {
            Write-Check $check.Key "PASS"
        } else {
            Write-Check $check.Key "FAIL"
        }
    }
} else {
    Write-Check "Nginx configuration missing" "FAIL"
}

# 5. Check Docker Configuration
Write-Host "`n🐳 Checking Docker Configuration..." -ForegroundColor Cyan

if (-not $SkipDocker) {
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-Check "Docker installed: $dockerVersion" "PASS"
        } else {
            Write-Check "Docker not found" "FAIL" "Docker is required for deployment"
        }
        
        $composeVersion = docker-compose --version 2>$null
        if ($composeVersion) {
            Write-Check "Docker Compose installed: $composeVersion" "PASS"
        } else {
            Write-Check "Docker Compose not found" "FAIL" "Docker Compose is required for deployment"
        }
    } catch {
        Write-Check "Docker check failed" "FAIL" $_.Exception.Message
    }
} else {
    Write-Check "Docker check skipped" "WARN"
}

# 6. Check Admin Panel Configuration
Write-Host "`n👤 Checking Admin Panel Configuration..." -ForegroundColor Cyan

if (Test-Path "soleva back end/scripts/setup.py") {
    $setupScript = Get-Content "soleva back end/scripts/setup.py"
    
    $adminChecks = @{
        "Admin username configured" = $setupScript -match "soleva_admin"
        "Admin email configured" = $setupScript -match "admin@solevaeg.com"
        "Admin password configured" = $setupScript -match "\?3aeeSjqq"
    }
    
    foreach ($check in $adminChecks.GetEnumerator()) {
        if ($check.Value) {
            Write-Check $check.Key "PASS"
        } else {
            Write-Check $check.Key "FAIL"
        }
    }
} else {
    Write-Check "Setup script missing" "FAIL"
}

# 7. Check Frontend Configuration
Write-Host "`n⚛️ Checking Frontend Configuration..." -ForegroundColor Cyan

if (Test-Path "soleva front end/package.json") {
    $packageJson = Get-Content "soleva front end/package.json" | ConvertFrom-Json
    
    $frontendChecks = @{
        "React project configured" = $packageJson.dependencies.react -ne $null
        "Build script present" = $packageJson.scripts.build -ne $null
        "TypeScript configured" = $packageJson.devDependencies.typescript -ne $null
        "Vite configured" = $packageJson.devDependencies.vite -ne $null
    }
    
    foreach ($check in $frontendChecks.GetEnumerator()) {
        if ($check.Value) {
            Write-Check $check.Key "PASS"
        } else {
            Write-Check $check.Key "WARN"
        }
    }
} else {
    Write-Check "Frontend package.json missing" "FAIL"
}

# 8. Check Backend Configuration
Write-Host "`n🐍 Checking Backend Configuration..." -ForegroundColor Cyan

if (Test-Path "soleva back end/requirements.txt") {
    $requirements = Get-Content "soleva back end/requirements.txt"
    
    $backendChecks = @{
        "Django configured" = $requirements -match "Django"
        "PostgreSQL adapter present" = $requirements -match "psycopg2"
        "Redis client present" = $requirements -match "redis"
        "Celery present" = $requirements -match "celery"
    }
    
    foreach ($check in $backendChecks.GetEnumerator()) {
        if ($check.Value) {
            Write-Check $check.Key "PASS"
        } else {
            Write-Check $check.Key "FAIL"
        }
    }
} else {
    Write-Check "Backend requirements.txt missing" "FAIL"
}

# 9. Security Checks
Write-Host "`n🔒 Security Configuration Checks..." -ForegroundColor Cyan

$securityChecks = @{
    "DEBUG disabled" = $envContent -match "DEBUG=False"
    "Strong database password" = ($envContent -match "DB_PASSWORD=") -and -not ($envContent -match "DB_PASSWORD=password")
    "Strong admin password" = $envContent -match "ADMIN_PASSWORD=\?3aeeSjqq"
    "SSL email configured" = $envContent -match "SSL_EMAIL=admin@solevaeg.com"
}

foreach ($check in $securityChecks.GetEnumerator()) {
    if ($check.Value) {
        Write-Check $check.Key "PASS"
    } else {
        Write-Check $check.Key "FAIL"
    }
}

# 10. Domain and SSL Configuration
Write-Host "`n🌍 Domain and SSL Configuration..." -ForegroundColor Cyan

$domainChecks = @{
    "Primary domain configured" = $envContent -match "DOMAIN=solevaeg.com"
    "SSL email configured" = $envContent -match "SSL_EMAIL=admin@solevaeg.com"
    "Allowed hosts configured" = $envContent -match "ALLOWED_HOSTS=.*solevaeg.com"
}

foreach ($check in $domainChecks.GetEnumerator()) {
    if ($check.Value) {
        Write-Check $check.Key "PASS"
    } else {
        Write-Check $check.Key "FAIL"
    }
}

# Summary
Write-Host "`n📊 Deployment Verification Summary" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

if ($ErrorCount -eq 0 -and $WarningCount -eq 0) {
    Write-Host "🎉 All checks passed! The website is ready for VPS deployment." -ForegroundColor Green
    Write-Host "`n🚀 Next Steps for Deployment:" -ForegroundColor Green
    Write-Host "1. Upload project files to your VPS" -ForegroundColor White
    Write-Host "2. Run: docker-compose up -d" -ForegroundColor White
    Write-Host "3. Run: docker-compose run --rm certbot" -ForegroundColor White
    Write-Host "4. Verify: https://solevaeg.com" -ForegroundColor White
    Write-Host "`n👤 Admin Access:" -ForegroundColor Green
    Write-Host "URL: https://solevaeg.com/admin/" -ForegroundColor White
    Write-Host "Username: soleva_admin" -ForegroundColor White
    Write-Host "Email: admin@solevaeg.com" -ForegroundColor White
    Write-Host "Password: ?3aeeSjqq" -ForegroundColor White
} elseif ($ErrorCount -eq 0) {
    Write-Host "⚠️ Deployment ready with $WarningCount warnings." -ForegroundColor Yellow
    Write-Host "Review warnings above and proceed with caution." -ForegroundColor Yellow
} else {
    Write-Host "❌ Deployment NOT ready. Found $ErrorCount errors and $WarningCount warnings." -ForegroundColor Red
    Write-Host "Please fix all errors before deploying." -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Verification completed!" -ForegroundColor Green
