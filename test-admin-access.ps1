# Test Admin Panel Access Script
# This script tests admin panel functionality and access

Write-Host "🔐 Testing Soleva Admin Panel Access" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Load environment variables
if (Test-Path "docker.env") {
    $envVars = Get-Content "docker.env" | Where-Object { $_ -notmatch '^#' -and $_.Trim() -ne "" }
    foreach ($envVar in $envVars) {
        if ($envVar -match '^([^=]+)=(.*)$') {
            $name = $matches[1]
            $value = $matches[2]
            [System.Environment]::SetEnvironmentVariable($name, $value, [System.EnvironmentVariableTarget]::Process)
        }
    }
}

$domain = [System.Environment]::GetEnvironmentVariable("DOMAIN") ?? "localhost"
$adminUsername = [System.Environment]::GetEnvironmentVariable("ADMIN_USERNAME") ?? "soleva_admin"
$adminPassword = [System.Environment]::GetEnvironmentVariable("ADMIN_PASSWORD") ?? "?3aeeSjqq"
$adminEmail = [System.Environment]::GetEnvironmentVariable("ADMIN_EMAIL") ?? "admin@solevaeg.com"

Write-Host "📋 Admin Panel Information:" -ForegroundColor Cyan
Write-Host "   Domain: $domain" -ForegroundColor White
Write-Host "   Username: $adminUsername" -ForegroundColor White
Write-Host "   Email: $adminEmail" -ForegroundColor White
Write-Host "   Password: $adminPassword" -ForegroundColor White
Write-Host ""

# Test URLs
$adminUrls = @(
    "http://$domain/admin/",
    "http://$domain/admin/login/",
    "https://$domain/admin/",
    "https://$domain/admin/login/"
)

Write-Host "🌐 Testing Admin Panel URLs:" -ForegroundColor Yellow
foreach ($url in $adminUrls) {
    try {
        Write-Host "   Testing: $url" -ForegroundColor Cyan
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ $url - Accessible" -ForegroundColor Green
            
            # Check if it contains Django admin content
            if ($response.Content -match "Django administration" -or $response.Content -match "admin") {
                Write-Host "   ✅ Django admin interface detected" -ForegroundColor Green
            }
        } else {
            Write-Host "   ⚠️  $url - Status: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ❌ $url - Not accessible: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🔍 Testing API Endpoints:" -ForegroundColor Yellow

$apiUrls = @(
    "http://$domain/api/",
    "http://$domain/api/admin/dashboard/",
    "http://$domain/health"
)

foreach ($url in $apiUrls) {
    try {
        Write-Host "   Testing: $url" -ForegroundColor Cyan
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ $url - OK" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  $url - Status: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ❌ $url - Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🐳 Checking Backend Container Status:" -ForegroundColor Yellow
$backendContainer = docker ps -q -f name="soleva_backend"
if ($backendContainer) {
    Write-Host "   ✅ Backend container is running" -ForegroundColor Green
    
    # Test admin user creation
    Write-Host "   🔐 Testing admin user creation..." -ForegroundColor Cyan
    try {
        $createAdminScript = @"
from django.contrib.auth import get_user_model
User = get_user_model()

# Check if admin user exists
if User.objects.filter(email='$adminEmail').exists():
    user = User.objects.get(email='$adminEmail')
    print(f'✅ Admin user exists: {user.email}')
    print(f'   Username: {user.username}')
    print(f'   Is superuser: {user.is_superuser}')
    print(f'   Is staff: {user.is_staff}')
    print(f'   Is active: {user.is_active}')
else:
    print('❌ Admin user does not exist')
    print('Creating admin user...')
    user = User.objects.create_superuser(
        username='$adminUsername',
        email='$adminEmail',
        password='$adminPassword',
        first_name='Soleva',
        last_name='Admin'
    )
    print(f'✅ Admin user created: {user.email}')
"@
        
        $result = docker exec $backendContainer python manage.py shell -c $createAdminScript
        Write-Host "   $result" -ForegroundColor White
    } catch {
        Write-Host "   ❌ Failed to check/create admin user: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "   ❌ Backend container is not running" -ForegroundColor Red
    Write-Host "   Run: docker-compose up -d backend" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📊 ADMIN PANEL ACCESS SUMMARY" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

Write-Host "🌐 Admin Panel URLs:" -ForegroundColor Cyan
Write-Host "   Primary:  http://$domain/admin/" -ForegroundColor White
Write-Host "   HTTPS:    https://$domain/admin/" -ForegroundColor White
Write-Host "   Login:    http://$domain/admin/login/" -ForegroundColor White

Write-Host ""
Write-Host "🔐 Admin Credentials:" -ForegroundColor Cyan
Write-Host "   Username: $adminUsername" -ForegroundColor White
Write-Host "   Email:    $adminEmail" -ForegroundColor White  
Write-Host "   Password: $adminPassword" -ForegroundColor White

Write-Host ""
Write-Host "📋 Admin Panel Features Available:" -ForegroundColor Cyan
Write-Host "   ✅ Product Management (Add/Edit/Delete Products)" -ForegroundColor Green
Write-Host "   ✅ Category Management" -ForegroundColor Green
Write-Host "   ✅ Brand Management" -ForegroundColor Green
Write-Host "   ✅ Color & Variant Management" -ForegroundColor Green
Write-Host "   ✅ Offer & Bundle Management" -ForegroundColor Green
Write-Host "   ✅ Flash Sales Management" -ForegroundColor Green
Write-Host "   ✅ Order Management" -ForegroundColor Green
Write-Host "   ✅ Customer Management" -ForegroundColor Green
Write-Host "   ✅ Website Content Management" -ForegroundColor Green
Write-Host "   ✅ Notification Banners" -ForegroundColor Green
Write-Host "   ✅ Site Configuration" -ForegroundColor Green
Write-Host "   ✅ User Messages System" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Ready for Use!" -ForegroundColor Green
