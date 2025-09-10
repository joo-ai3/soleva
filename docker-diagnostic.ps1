# Docker Diagnostic Script for Soleva
# Quickly checks the current state of Docker and containers

Write-Host "🔍 SOLEVA DOCKER DIAGNOSTIC" -ForegroundColor Cyan
Write-Host "============================"

# Check if Docker is running
Write-Host "`n🐳 Checking Docker status..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "✅ Docker is running: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker is not running or not installed" -ForegroundColor Red
        Write-Host "   Please start Docker Desktop first" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Docker is not available" -ForegroundColor Red
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker compose version 2>$null
    if ($composeVersion) {
        Write-Host "✅ Docker Compose is available" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Docker Compose is not available" -ForegroundColor Red
}

# Check for docker-compose.yml
if (Test-Path "docker-compose.yml") {
    Write-Host "✅ docker-compose.yml found" -ForegroundColor Green
} else {
    Write-Host "❌ docker-compose.yml not found" -ForegroundColor Red
    Write-Host "   Please run this script from the project root directory" -ForegroundColor Yellow
    exit 1
}

# Check environment file
Write-Host "`n📄 Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path "docker.env") {
    Write-Host "✅ docker.env file exists" -ForegroundColor Green

    # Check critical environment variables
    $envContent = Get-Content "docker.env" -ErrorAction SilentlyContinue
    $requiredVars = @("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD", "REDIS_PASSWORD")

    foreach ($var in $requiredVars) {
        $found = $envContent | Where-Object { $_ -match "^$var=" }
        if ($found) {
            Write-Host "✅ $var is configured" -ForegroundColor Green
        } else {
            Write-Host "❌ $var is missing" -ForegroundColor Red
        }
    }
} else {
    Write-Host "❌ docker.env file not found" -ForegroundColor Red
    if (Test-Path "docker.env.example") {
        Write-Host "   Found docker.env.example - you may need to copy it" -ForegroundColor Yellow
    }
}

# Check current container status
Write-Host "`n📦 Checking container status..." -ForegroundColor Yellow
try {
    $containers = docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>$null
    if ($containers) {
        Write-Host "Current containers:" -ForegroundColor Cyan
        Write-Host $containers
    } else {
        Write-Host "No containers found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Could not check container status" -ForegroundColor Red
}

# Check for orphan containers
Write-Host "`n👻 Checking for orphan containers..." -ForegroundColor Yellow
try {
    $orphanContainers = docker ps -a --filter "label=com.docker.compose.project=soleva" --format "{{.Names}}" 2>$null
    if ($orphanContainers) {
        Write-Host "Found potential orphan containers:" -ForegroundColor Yellow
        $orphanContainers | ForEach-Object {
            Write-Host "  - $_" -ForegroundColor Red
        }
        Write-Host "💡 Run cleanup script to remove orphans" -ForegroundColor Cyan
    } else {
        Write-Host "✅ No orphan containers detected" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Could not check for orphan containers" -ForegroundColor Red
}

# Check Docker networks
Write-Host "`n🌐 Checking Docker networks..." -ForegroundColor Yellow
try {
    $networks = docker network ls --format "{{.Name}}" | Where-Object { $_ -match "soleva" }
    if ($networks) {
        Write-Host "Found Soleva networks:" -ForegroundColor Green
        $networks | ForEach-Object {
            Write-Host "  - $_" -ForegroundColor Green
        }
    } else {
        Write-Host "No Soleva networks found (this is normal if services aren't running)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Could not check networks" -ForegroundColor Red
}

# Check Docker volumes
Write-Host "`n💾 Checking Docker volumes..." -ForegroundColor Yellow
try {
    $volumes = docker volume ls --format "{{.Name}}" | Where-Object { $_ -match "soleva" }
    if ($volumes) {
        Write-Host "Found Soleva volumes:" -ForegroundColor Green
        $volumes | ForEach-Object {
            Write-Host "  - $_" -ForegroundColor Green
        }
    } else {
        Write-Host "No Soleva volumes found (this is normal if services haven't been started)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Could not check volumes" -ForegroundColor Red
}

Write-Host "`n🎯 DIAGNOSTIC COMPLETE" -ForegroundColor Cyan
Write-Host "======================"

Write-Host "`n💡 Next steps:" -ForegroundColor Yellow
Write-Host "1. If Docker is not running, start Docker Desktop"
Write-Host "2. If environment variables are missing, check docker.env"
Write-Host "3. If you see orphan containers, run the cleanup script"
Write-Host "4. Run the cleanup and startup script: .\docker-cleanup-and-start.ps1"

Write-Host "`n🚀 Ready to fix issues? Run: .\docker-cleanup-and-start.ps1" -ForegroundColor Green
