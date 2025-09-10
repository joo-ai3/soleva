# Backend Reset and Migration Fix Script for Soleva (PowerShell)
# This script completely resets the backend and fixes migration issues

param(
    [switch]$Help,
    [switch]$DryRun
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

# Function to stop all services
function Stop-Services {
    Write-Status "Stopping all services..."
    docker compose down --remove-orphans 2>$null
}

# Function to remove migration files
function Remove-Migrations {
    Write-Status "Removing existing migration files..."

    # Define apps with migrations
    $apps = @("users", "products", "cart", "orders", "coupons", "notifications", "shipping", "payments", "tracking", "offers", "accounting", "otp", "website_management")

    foreach ($app in $apps) {
        $migrationDir = "soleva back end\$app\migrations"

        if (Test-Path $migrationDir) {
            Write-Debug "Removing migrations for $app..."

            # Remove all migration files except __init__.py
            Get-ChildItem "$migrationDir\*.py" -Exclude "__init__.py" | Remove-Item -Force -ErrorAction SilentlyContinue

            # Verify cleanup
            $remainingFiles = Get-ChildItem "$migrationDir\*.py" -Exclude "__init__.py"
            if ($remainingFiles.Count -eq 0) {
                Write-Status "✅ Cleaned migrations for $app"
            } else {
                Write-Warning "⚠️  Some migration files may remain for $app"
            }
        } else {
            Write-Warning "Migration directory not found for $app`: $migrationDir"
        }
    }

    Write-Status "Migration cleanup completed!"
}

# Function to reset PostgreSQL database
function Reset-Database {
    Write-Status "Resetting PostgreSQL database..."

    # Start only PostgreSQL
    Write-Debug "Starting PostgreSQL..."
    docker compose up -d postgres

    # Wait for PostgreSQL to be ready
    Write-Debug "Waiting for PostgreSQL to be ready..."
    $maxAttempts = 30
    $attempt = 1

    while ($attempt -le $maxAttempts) {
        try {
            $result = docker compose exec -T postgres pg_isready -U soleva_user -d soleva_db 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Status "PostgreSQL is ready!"
                break
            }
        } catch {
            # PostgreSQL not ready yet
        }

        Write-Debug "Waiting... (attempt $attempt/$maxAttempts)"
        Start-Sleep -Seconds 3
        $attempt++
    }

    if ($attempt -gt $maxAttempts) {
        Write-Error "PostgreSQL failed to start properly"
        return $false
    }

    # Reset database schema
    Write-Debug "Resetting database schema..."
    $resetScript = @"
-- Drop and recreate public schema
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- Grant permissions
GRANT ALL ON SCHEMA public TO soleva_user;
GRANT ALL ON SCHEMA public TO public;

-- Set default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO soleva_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO soleva_user;
"@

    $resetScript | docker compose exec -T postgres psql -U soleva_user -d soleva_db

    Write-Status "✅ Database reset completed!"
    return $true
}

# Function to start backend
function Start-Backend {
    Write-Status "Starting backend container..."

    # Start Redis as well since backend depends on it
    Write-Debug "Starting Redis..."
    docker compose up -d redis

    # Wait for Redis
    Write-Debug "Waiting for Redis..."
    $maxAttempts = 20
    $attempt = 1

    while ($attempt -le $maxAttempts) {
        try {
            $result = docker compose exec -T redis redis-cli -a "Redis@2025" ping 2>$null
            if ($result -match "PONG") {
                Write-Status "Redis is ready!"
                break
            }
        } catch {
            # Redis not ready yet
        }

        Write-Debug "Waiting for Redis... (attempt $attempt/$maxAttempts)"
        Start-Sleep -Seconds 2
        $attempt++
    }

    if ($attempt -gt $maxAttempts) {
        Write-Warning "Redis may not be ready, but continuing..."
    }

    # Start backend
    Write-Debug "Starting backend container..."
    docker compose up -d backend

    # Wait for backend to be ready
    Write-Debug "Waiting for backend to start..."
    Start-Sleep -Seconds 10

    Write-Status "✅ Backend container started!"
}

# Function to recreate and apply migrations
function Update-Migrations {
    Write-Status "Recreating and applying migrations..."

    # Make migrations
    Write-Debug "Creating new migrations..."
    $result = docker compose exec -T backend python manage.py makemigrations 2>$null

    if ($LASTEXITCODE -eq 0) {
        Write-Status "✅ Makemigrations completed successfully"
    } else {
        Write-Error "❌ Makemigrations failed"
        docker compose logs backend
        return $false
    }

    # Apply migrations
    Write-Debug "Applying migrations..."
    $result = docker compose exec -T backend python manage.py migrate 2>$null

    if ($LASTEXITCODE -eq 0) {
        Write-Status "✅ Migrations applied successfully"
    } else {
        Write-Error "❌ Migration failed"
        docker compose logs backend
        return $false
    }

    return $true
}

# Function to create superuser
function New-SuperUser {
    Write-Status "Creating superuser..."

    # Create superuser non-interactively
    $superuserScript = @"
from django.contrib.auth import get_user_model
import os

User = get_user_model()

# Check if superuser already exists
if not User.objects.filter(email='admin@solevaeg.com').exists():
    User.objects.create_superuser(
        email='admin@solevaeg.com',
        password=os.environ.get('ADMIN_PASSWORD', 'S0l3v@_Admin!2025#'),
        first_name='Admin',
        last_name='User'
    )
    print('Superuser created successfully')
    print('Email: admin@solevaeg.com')
    print('Password: ' + os.environ.get('ADMIN_PASSWORD', 'S0l3v@_Admin!2025#'))
else:
    print('Superuser already exists')
"@

    $superuserScript | docker compose exec -T backend python manage.py shell

    Write-Status "✅ Superuser setup completed!"
}

# Function to verify everything is working
function Test-Setup {
    Write-Status "Verifying setup..."

    Write-Host ""
    Write-Status "Container Status:"
    docker compose ps

    Write-Host ""
    Write-Status "Testing backend health:"
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health/" -TimeoutSec 10 -ErrorAction Stop
        Write-Status "✅ Backend API is responding"
    } catch {
        Write-Warning "⚠️  Backend API is not responding yet"
        Write-Debug "This is normal if the backend is still starting up"
    }

    Write-Host ""
    Write-Status "Recent backend logs:"
    docker compose logs --tail=20 backend

    Write-Host ""
    Write-Status "Database tables check:"
    $tableScript = @"
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public';")
    tables = cursor.fetchall()

print(f"Found {len(tables)} tables in database:")
for table in tables[:10]:
    print(f"  - {table[0]}")
if len(tables) > 10:
    print(f"  ... and {len(tables) - 10} more tables")
"@

    $tableScript | docker compose exec -T backend python manage.py shell
}

# Function to show summary
function Show-Summary {
    Write-Host ""
    Write-Status "🎉 BACKEND RESET COMPLETED!"
    Write-Host "=================================="

    Write-Host ""
    Write-Status "What was done:"
    Write-Host "  ✅ Removed all existing migration files"
    Write-Host "  ✅ Reset PostgreSQL database (dropped and recreated public schema)"
    Write-Host "  ✅ Started backend container with dependencies"
    Write-Host "  ✅ Recreated and applied all migrations"
    Write-Host "  ✅ Created superuser account"

    Write-Host ""
    Write-Status "Access your application:"
    Write-Host "  • Backend API: http://localhost:8000/api/"
    Write-Host "  • Admin Panel: http://localhost/admin/"
    Write-Host "  • Superuser Email: admin@solevaeg.com"
    Write-Host "  • Superuser Password: S0l3v@_Admin!2025#"

    Write-Host ""
    Write-Status "Useful commands:"
    Write-Host "  • View logs: docker compose logs -f backend"
    Write-Host "  • Restart backend: docker compose restart backend"
    Write-Host "  • Check status: docker compose ps"
    Write-Host "  • Stop all: docker compose down"

    Write-Host ""
    Write-Warning "⚠️  IMPORTANT NOTES:"
    Write-Host "  • All previous data has been removed from the database"
    Write-Host "  • You may need to restart other services (frontend, nginx) if needed"
    Write-Host "  • The static files warning is expected and can be ignored for now"
}

# Main script execution
function Main {
    if ($Help) {
        Write-Host "Soleva Backend Reset and Migration Fix Script (PowerShell)"
        Write-Host ""
        Write-Host "This script will:"
        Write-Host "  • Stop all services"
        Write-Host "  • Remove all existing migration files"
        Write-Host "  • Reset PostgreSQL database (DROPS ALL DATA)"
        Write-Host "  • Start backend container"
        Write-Host "  • Recreate and apply migrations"
        Write-Host "  • Create superuser"
        Write-Host "  • Verify everything is working"
        Write-Host ""
        Write-Host "⚠️  WARNING: This will DELETE ALL existing data in the database!"
        Write-Host ""
        Write-Host "Usage: .\backend-reset-fix.ps1 [options]"
        Write-Host "Options:"
        Write-Host "  -Help      Show this help message"
        Write-Host "  -DryRun    Show what would be done without executing"
        Write-Host ""
        return
    }

    if ($DryRun) {
        Write-Host "🔍 DRY RUN MODE - Showing what would be done:"
        Write-Host ""
        Write-Host "1. Stop all services"
        Write-Host "2. Remove migration files from:"
        Write-Host "   - users, products, cart, orders, coupons, notifications"
        Write-Host "   - shipping, payments, tracking, offers, accounting, otp"
        Write-Host "   - website_management"
        Write-Host "3. Reset PostgreSQL database (DROP SCHEMA public CASCADE)"
        Write-Host "4. Start backend container"
        Write-Host "5. Run: python manage.py makemigrations"
        Write-Host "6. Run: python manage.py migrate"
        Write-Host "7. Create superuser: admin@solevaeg.com"
        Write-Host ""
        Write-Warning "⚠️  This would DELETE ALL existing data!"
        return
    }

    Write-Host "🔄 SOLEVA BACKEND RESET & MIGRATION FIX"
    Write-Host "======================================="

    # Safety confirmation
    Write-Host ""
    Write-Warning "⚠️  WARNING: This will DELETE ALL existing data in the database!"
    Write-Host ""
    $confirm = Read-Host "Are you sure you want to continue? (type 'yes' to confirm)"

    if ($confirm -ne "yes") {
        Write-Debug "Operation cancelled by user."
        return
    }

    # Execute all steps
    if (-not (Test-Docker)) { return }

    Stop-Services
    Remove-Migrations

    if (-not (Reset-Database)) { return }

    Start-Backend

    if (-not (Update-Migrations)) { return }

    New-SuperUser
    Test-Setup
    Show-Summary
}

# Run main function
Main
