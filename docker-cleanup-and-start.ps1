# Comprehensive Docker Cleanup and Startup Script for Soleva (PowerShell)
# This script fixes backend connection issues and removes orphan containers

param(
    [switch]$Help
)

# Function to print colored output
function Write-Status($Message) {
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning($Message) {
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error($Message) {
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Debug($Message) {
    Write-Host "[DEBUG] $Message" -ForegroundColor Blue
}

# Function to check if Docker is running
function Test-Docker {
    Write-Status "Checking Docker status..."
    try {
        $dockerVersion = docker --version 2>$null
        $composeVersion = docker compose version 2>$null

        if (-not $dockerVersion -or -not $composeVersion) {
            throw "Docker or Docker Compose not available"
        }

        Write-Status "Docker is ready!"
        return $true
    }
    catch {
        Write-Error "Docker is not installed or not running"
        Write-Error "Please ensure Docker Desktop is running"
        return $false
    }
}

# Function to clean up orphan containers and resources
function Clear-DockerResources {
    Write-Status "Cleaning up Docker resources..."

    # Stop all running containers
    Write-Debug "Stopping all containers..."
    docker compose down --remove-orphans 2>$null

    # Remove orphan containers
    Write-Debug "Removing orphan containers..."
    docker compose down --remove-orphans --volumes 2>$null

    # Clean up unused containers, networks, and images
    Write-Debug "Cleaning up unused Docker resources..."
    docker system prune -f

    # Remove any leftover containers with 'soleva' in the name
    Write-Debug "Removing any leftover Soleva containers..."
    $containers = docker ps -a --filter "name=soleva" --format "{{.Names}}" 2>$null
    if ($containers) {
        $containers | ForEach-Object {
            Write-Debug "Removing container: $_"
            docker rm -f $_ 2>$null
        }
    }

    Write-Status "Cleanup completed!"
}

# Function to verify environment configuration
function Test-Environment {
    Write-Status "Verifying environment configuration..."

    # Check if docker.env exists
    if (-not (Test-Path "docker.env")) {
        Write-Error "docker.env file not found!"
        Write-Debug "Creating docker.env from docker.env.example..."

        if (Test-Path "docker.env.example") {
            Copy-Item "docker.env.example" "docker.env"
            Write-Warning "Please update docker.env with your actual configuration values"
        } else {
            Write-Error "Neither docker.env nor docker.env.example found"
            return $false
        }
    }

    # Verify critical environment variables
    $requiredVars = @("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD", "REDIS_PASSWORD")
    $missingVars = @()

    $envContent = Get-Content "docker.env" -ErrorAction SilentlyContinue

    foreach ($var in $requiredVars) {
        $found = $envContent | Where-Object { $_ -match "^$var=" }
        if (-not $found) {
            $missingVars += $var
        }
    }

    if ($missingVars.Count -gt 0) {
        Write-Error "Missing required environment variables: $($missingVars -join ', ')"
        Write-Debug "Please check your docker.env file"
        return $false
    }

    Write-Status "Environment configuration is valid!"
    return $true
}

# Function to start services in correct order
function Start-SolevaServices {
    Write-Status "Starting Soleva services..."

    # Start only database and Redis first
    Write-Debug "Starting database and Redis services..."
    docker compose up -d postgres redis

    # Wait for database and Redis to be healthy
    Write-Debug "Waiting for database and Redis to be ready..."
    $maxAttempts = 30
    $attempt = 1

    while ($attempt -le $maxAttempts) {
        Write-Debug "Health check attempt $attempt/$maxAttempts..."

        $postgresReady = $false
        $redisReady = $false

        # Check PostgreSQL
        try {
            $postgresResult = docker compose exec -T postgres pg_isready -U soleva_user -d soleva_db 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Status "PostgreSQL is ready!"
                $postgresReady = $true
            }
        } catch {
            # PostgreSQL not ready yet
        }

        # Check Redis
        try {
            $redisResult = docker compose exec -T redis redis-cli -a "Redis@2025" ping 2>$null
            if ($redisResult -match "PONG") {
                Write-Status "Redis is ready!"
                $redisReady = $true
            }
        } catch {
            # Redis not ready yet
        }

        if ($postgresReady -and $redisReady) {
            Write-Status "All dependencies are ready!"
            break
        }

        Start-Sleep -Seconds 5
        $attempt++
    }

    if ($attempt -gt $maxAttempts) {
        Write-Error "Database and/or Redis failed to start properly"
        docker compose logs postgres redis
        return $false
    }

    # Start backend
    Write-Debug "Starting backend service..."
    docker compose up -d backend

    # Wait for backend to be ready
    Write-Debug "Waiting for backend to be ready..."
    $maxAttempts = 20
    $attempt = 1

    while ($attempt -le $maxAttempts) {
        Write-Debug "Backend health check attempt $attempt/$maxAttempts..."

        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health/" -TimeoutSec 10 -ErrorAction Stop
            Write-Status "Backend is ready!"
            break
        } catch {
            Start-Sleep -Seconds 5
            $attempt++
        }
    }

    if ($attempt -gt $maxAttempts) {
        Write-Error "Backend failed to start properly"
        docker compose logs backend
        return $false
    }

    # Start remaining services
    Write-Debug "Starting remaining services..."
    docker compose up -d frontend nginx celery celery-beat

    Write-Status "All services started successfully!"
    return $true
}

# Function to verify everything is working
function Test-Services {
    Write-Status "Verifying service status..."

    Write-Host ""
    docker compose ps

    Write-Host ""
    Write-Status "Testing service health:"

    # Test backend API
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health/" -TimeoutSec 10 -ErrorAction Stop
        Write-Status "✅ Backend API is responding"
    } catch {
        Write-Warning "⚠️  Backend API is not responding yet"
    }

    # Test frontend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000/" -TimeoutSec 10 -ErrorAction Stop
        Write-Status "✅ Frontend is responding"
    } catch {
        Write-Warning "⚠️  Frontend is not responding yet"
    }

    # Test nginx
    try {
        $response = Invoke-WebRequest -Uri "http://localhost/" -TimeoutSec 10 -ErrorAction Stop
        Write-Status "✅ Nginx reverse proxy is working"
    } catch {
        Write-Warning "⚠️  Nginx is not responding yet"
    }

    Write-Host ""
    Write-Status "Useful commands:"
    Write-Host "  • View logs:           docker compose logs -f"
    Write-Host "  • Stop services:       docker compose down"
    Write-Host "  • Restart backend:     docker compose restart backend"
    Write-Host "  • View running status: docker compose ps"
    Write-Host "  • Clean restart:       .\docker-cleanup-and-start.ps1"
}

# Main script
function Main {
    if ($Help) {
        Write-Host "Soleva Docker Cleanup and Startup Script (PowerShell)"
        Write-Host "Usage: .\docker-cleanup-and-start.ps1 [options]"
        Write-Host ""
        Write-Host "This script:"
        Write-Host "  • Cleans up orphan containers and resources"
        Write-Host "  • Verifies environment configuration"
        Write-Host "  • Starts services in correct order (database → Redis → backend → others)"
        Write-Host "  • Ensures all services are healthy before proceeding"
        Write-Host "  • Provides verification of the running system"
        Write-Host ""
        Write-Host "Options:"
        Write-Host "  -Help    Show this help message"
        Write-Host ""
        return
    }

    Write-Status "🚀 SOLEVA DOCKER CLEANUP AND STARTUP"
    Write-Host "======================================"

    # Change to project root if needed
    if (-not (Test-Path "docker-compose.yml")) {
        Write-Error "docker-compose.yml not found in current directory"
        Write-Debug "Please run this script from the project root directory"
        return
    }

    if (-not (Test-Docker)) { return }
    Clear-DockerResources

    if (-not (Test-Environment)) { return }

    if (-not (Start-SolevaServices)) { return }

    Test-Services

    Write-Host ""
    Write-Status "🎉 SOLEVA IS NOW RUNNING SUCCESSFULLY!"
    Write-Debug "Access your application at:"
    Write-Host "  • Frontend: http://localhost"
    Write-Host "  • Backend API: http://localhost/api/"
    Write-Host "  • Admin Panel: http://localhost/admin/"
}

# Run main function
Main
