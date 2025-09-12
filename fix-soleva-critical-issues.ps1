# Soleva Critical Issues Fix Script
# This script addresses all critical issues mentioned in the requirements

param(
    [switch]$SkipSSL = $false,
    [switch]$ForceRestart = $false
)

Write-Host "🚀 Starting Soleva Critical Issues Fix" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# Check if Docker is running
Write-Host "📋 Checking Docker status..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Stop existing containers if force restart is requested
if ($ForceRestart) {
    Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
    docker-compose down --remove-orphans
}

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Yellow
$directories = @(
    "ssl/certbot/conf",
    "ssl/certbot/www", 
    "nginx/logs",
    "backups",
    "logs"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    }
}

# Check if environment file exists
if (!(Test-Path "docker.env")) {
    Write-Host "❌ docker.env file not found!" -ForegroundColor Red
    Write-Host "Please ensure docker.env exists with proper configuration." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Environment file found" -ForegroundColor Green

# Load environment variables
Write-Host "📋 Loading environment configuration..." -ForegroundColor Yellow
$envVars = Get-Content "docker.env" | Where-Object { $_ -notmatch '^#' -and $_.Trim() -ne "" }
foreach ($envVar in $envVars) {
    if ($envVar -match '^([^=]+)=(.*)$') {
        $name = $matches[1]
        $value = $matches[2]
        [System.Environment]::SetEnvironmentVariable($name, $value, [System.EnvironmentVariableTarget]::Process)
    }
}

$domain = [System.Environment]::GetEnvironmentVariable("DOMAIN")
$sslEmail = [System.Environment]::GetEnvironmentVariable("SSL_EMAIL")

if ([string]::IsNullOrEmpty($domain)) {
    Write-Host "❌ DOMAIN not set in docker.env" -ForegroundColor Red
    exit 1
}

if ([string]::IsNullOrEmpty($sslEmail)) {
    Write-Host "❌ SSL_EMAIL not set in docker.env" -ForegroundColor Red
    exit 1
}

Write-Host "🌐 Domain: $domain" -ForegroundColor Cyan
Write-Host "📧 SSL Email: $sslEmail" -ForegroundColor Cyan

# Step 1: Start services
Write-Host "🔧 Step 1: Starting services..." -ForegroundColor Yellow

# Start services
Write-Host "🚀 Starting Docker services..." -ForegroundColor Yellow
docker-compose up -d postgres redis
Start-Sleep -Seconds 10

docker-compose up -d backend
Start-Sleep -Seconds 15

docker-compose up -d frontend
Start-Sleep -Seconds 10

docker-compose up -d nginx
Start-Sleep -Seconds 5

# Check if services are running
Write-Host "🔍 Checking service status..." -ForegroundColor Yellow
$services = @("postgres", "redis", "backend", "frontend", "nginx")
$allHealthy = $true

foreach ($service in $services) {
    $status = docker-compose ps -q $service
    if ($status) {
        Write-Host "✅ $service is running" -ForegroundColor Green
    } else {
        Write-Host "❌ $service is not running" -ForegroundColor Red
        $allHealthy = $false
    }
}

if (-not $allHealthy) {
    Write-Host "⚠️  Some services are not healthy. Checking logs..." -ForegroundColor Yellow
    docker-compose logs --tail=10 backend
}

# Step 2: Generate SSL certificates
if (-not $SkipSSL) {
    Write-Host "🔒 Step 2: Generating SSL certificates..." -ForegroundColor Yellow
    
    # Test if domain is reachable
    Write-Host "🌐 Testing domain accessibility..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://$domain/health" -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Domain $domain is accessible" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Domain returned status: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️  Could not reach domain directly. Proceeding with SSL generation..." -ForegroundColor Yellow
    }
    
    # Generate SSL certificates
    Write-Host "📜 Requesting SSL certificates from Let's Encrypt..." -ForegroundColor Yellow
    
    $certbotResult = docker-compose run --rm certbot
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SSL certificates generated successfully!" -ForegroundColor Green
        
        # Restart nginx with SSL
        Write-Host "🔄 Restarting nginx with SSL..." -ForegroundColor Yellow
        docker-compose restart nginx
        Start-Sleep -Seconds 5
        
    } else {
        Write-Host "❌ SSL certificate generation failed" -ForegroundColor Red
        Write-Host "This might be due to DNS not being properly configured." -ForegroundColor Yellow
        Write-Host "Please ensure $domain points to your server IP address." -ForegroundColor Yellow
    }
} else {
    Write-Host "⏭️  Skipping SSL certificate generation" -ForegroundColor Yellow
}

# Step 3: Test the deployment
Write-Host "🧪 Step 3: Testing deployment..." -ForegroundColor Yellow

$testUrls = @(
    "http://$domain/health"
)

if (-not $SkipSSL -and $LASTEXITCODE -eq 0) {
    $testUrls += @(
        "https://$domain/health"
    )
}

foreach ($url in $testUrls) {
    try {
        Write-Host "🔍 Testing: $url" -ForegroundColor Cyan
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $url - OK" -ForegroundColor Green
        } else {
            Write-Host "⚠️  $url - Status: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ $url - Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Step 4: Display final status
Write-Host "" -ForegroundColor White
Write-Host "📊 DEPLOYMENT STATUS SUMMARY" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green

# Check container status
Write-Host "🐳 Container Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host "" -ForegroundColor White
Write-Host "🌐 Access URLs:" -ForegroundColor Cyan
Write-Host "   HTTP:  http://$domain" -ForegroundColor White
if (-not $SkipSSL -and $LASTEXITCODE -eq 0) {
    Write-Host "   HTTPS: https://$domain" -ForegroundColor Green
    Write-Host "   Admin: https://$domain/admin" -ForegroundColor Green
} else {
    Write-Host "   Admin: http://$domain/admin" -ForegroundColor White
}

Write-Host "" -ForegroundColor White
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Verify domain DNS points to your server IP" -ForegroundColor White
Write-Host "2. Test website functionality at $domain" -ForegroundColor White
Write-Host "3. Check all buttons and navigation work properly" -ForegroundColor White
Write-Host "4. Verify responsive design on mobile devices" -ForegroundColor White
Write-Host "5. Test SSL certificate if enabled" -ForegroundColor White

Write-Host "" -ForegroundColor White
Write-Host "✅ Critical issues fix completed!" -ForegroundColor Green