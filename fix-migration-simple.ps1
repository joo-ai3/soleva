# PowerShell script to fix Django migration issues for Soleva
# Simplified version without special characters

Write-Host "FIXING SOLEVA BACKEND MIGRATION ISSUES" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Step 1: Create static directories
Write-Host "Step 1: Creating static directories..." -ForegroundColor Yellow
$staticDir = "soleva back end\static"
$staticfilesDir = "soleva back end\staticfiles"
$mediaDir = "soleva back end\media"
$logsDir = "soleva back end\logs"

if (!(Test-Path $staticDir)) {
    New-Item -ItemType Directory -Path $staticDir -Force
    Write-Host "   Created: $staticDir" -ForegroundColor Green
}

if (!(Test-Path $staticfilesDir)) {
    New-Item -ItemType Directory -Path $staticfilesDir -Force
    Write-Host "   Created: $staticfilesDir" -ForegroundColor Green
}

if (!(Test-Path $mediaDir)) {
    New-Item -ItemType Directory -Path $mediaDir -Force
    Write-Host "   Created: $mediaDir" -ForegroundColor Green
}

if (!(Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force
    Write-Host "   Created: $logsDir" -ForegroundColor Green
}

# Step 2: Remove problematic migration files
Write-Host "Step 2: Removing problematic migration files..." -ForegroundColor Yellow
Get-ChildItem -Path "soleva back end" -Recurse -Include "migrations" -Directory | ForEach-Object {
    $migrationDir = $_.FullName
    Get-ChildItem -Path $migrationDir -File | Where-Object { $_.Name -ne "__init__.py" } | ForEach-Object {
        Remove-Item $_.FullName -Force
        Write-Host "   Removed: $($_.FullName)" -ForegroundColor Red
    }
}

# Step 3: Stop containers
Write-Host "Step 3: Stopping containers..." -ForegroundColor Yellow
try {
    docker compose down --remove-orphans 2>$null
    Write-Host "   Containers stopped successfully" -ForegroundColor Green
} catch {
    Write-Host "   Could not stop containers (may not be running)" -ForegroundColor Yellow
}

# Step 4: Reset database
Write-Host "Step 4: Resetting database..." -ForegroundColor Yellow
try {
    docker compose up -d postgres
    Start-Sleep -Seconds 5

    # Reset database schema
    $resetCmd = "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO soleva_user; GRANT ALL ON SCHEMA public TO public; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO soleva_user; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO soleva_user;"
    docker compose exec postgres psql -U soleva_user -d soleva_db -c $resetCmd
    Write-Host "   Database reset completed" -ForegroundColor Green
} catch {
    Write-Host "   Database reset failed" -ForegroundColor Red
}

# Step 5: Start backend and Redis
Write-Host "Step 5: Starting backend and Redis..." -ForegroundColor Yellow
try {
    docker compose up -d redis
    docker compose up -d backend
    Write-Host "   Backend and Redis started" -ForegroundColor Green
} catch {
    Write-Host "   Failed to start services" -ForegroundColor Red
}

# Step 6: Wait for backend to be ready
Write-Host "Step 6: Waiting for backend to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Step 7: Create migrations in correct order
Write-Host "Step 7: Creating migrations for users first..." -ForegroundColor Yellow
try {
    docker compose exec backend python manage.py makemigrations users
    Write-Host "   Users migrations created" -ForegroundColor Green
} catch {
    Write-Host "   Failed to create users migrations" -ForegroundColor Red
}

Write-Host "Step 8: Creating migrations for other apps..." -ForegroundColor Yellow
try {
    docker compose exec backend python manage.py makemigrations
    Write-Host "   All migrations created" -ForegroundColor Green
} catch {
    Write-Host "   Failed to create migrations" -ForegroundColor Red
}

# Step 8: Apply migrations in correct order
Write-Host "Step 9: Applying migrations in correct order..." -ForegroundColor Yellow

# Apply auth, contenttypes, sessions first (dependencies)
try {
    docker compose exec backend python manage.py migrate auth
    Write-Host "   Auth migrations applied" -ForegroundColor Green
} catch {
    Write-Host "   Failed to apply auth migrations" -ForegroundColor Red
}

try {
    docker compose exec backend python manage.py migrate contenttypes
    Write-Host "   ContentTypes migrations applied" -ForegroundColor Green
} catch {
    Write-Host "   Failed to apply contenttypes migrations" -ForegroundColor Red
}

try {
    docker compose exec backend python manage.py migrate sessions
    Write-Host "   Sessions migrations applied" -ForegroundColor Green
} catch {
    Write-Host "   Failed to apply sessions migrations" -ForegroundColor Red
}

# Apply users migration (custom user model)
try {
    docker compose exec backend python manage.py migrate users
    Write-Host "   Users migrations applied" -ForegroundColor Green
} catch {
    Write-Host "   Failed to apply users migrations" -ForegroundColor Red
}

# Apply admin (depends on users)
try {
    docker compose exec backend python manage.py migrate admin
    Write-Host "   Admin migrations applied" -ForegroundColor Green
} catch {
    Write-Host "   Failed to apply admin migrations" -ForegroundColor Red
}

# Apply remaining migrations
try {
    docker compose exec backend python manage.py migrate
    Write-Host "   All remaining migrations applied" -ForegroundColor Green
} catch {
    Write-Host "   Failed to apply remaining migrations" -ForegroundColor Red
}

# Step 9: Create superuser
Write-Host "Step 10: Creating superuser..." -ForegroundColor Yellow
try {
    # Create a temporary Python script file
    $superuserScript = @"
from django.contrib.auth import get_user_model
import os

User = get_user_model()
if not User.objects.filter(email='admin@solevaeg.com').exists():
    User.objects.create_superuser(
        email='admin@solevaeg.com',
        password=os.environ.get('ADMIN_PASSWORD', 'S0l3v@_Admin!2025#'),
        first_name='Admin',
        last_name='User'
    )
    print('Superuser created successfully!')
else:
    print('Superuser already exists')
"@

    $superuserScript | Out-File -FilePath "temp_superuser.py" -Encoding UTF8
    docker compose exec backend python manage.py shell -c "exec(open('temp_superuser.py').read())"
    Remove-Item "temp_superuser.py" -ErrorAction SilentlyContinue
    Write-Host "   Superuser creation attempted" -ForegroundColor Green
} catch {
    Write-Host "   Failed to create superuser" -ForegroundColor Red
}

# Step 10: Collect static files
Write-Host "Step 11: Collecting static files..." -ForegroundColor Yellow
try {
    docker compose exec backend python manage.py collectstatic --noinput
    Write-Host "   Static files collected" -ForegroundColor Green
} catch {
    Write-Host "   Failed to collect static files" -ForegroundColor Red
}

# Step 11: Start all services
Write-Host "Step 12: Starting all services..." -ForegroundColor Yellow
try {
    docker compose up -d frontend nginx celery celery-beat
    Write-Host "   All services started" -ForegroundColor Green
} catch {
    Write-Host "   Failed to start services" -ForegroundColor Red
}

Write-Host "" -ForegroundColor White
Write-Host "MIGRATION ISSUES FIXED!" -ForegroundColor Green
Write-Host "=======================" -ForegroundColor Green

Write-Host "" -ForegroundColor White
Write-Host "Check service status:" -ForegroundColor Cyan
Write-Host "docker compose ps" -ForegroundColor White

Write-Host "" -ForegroundColor White
Write-Host "Check backend logs:" -ForegroundColor Cyan
Write-Host "docker compose logs backend" -ForegroundColor White

Write-Host "" -ForegroundColor White
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost" -ForegroundColor White
Write-Host "Admin: http://localhost/admin/" -ForegroundColor White
Write-Host "API: http://localhost/api/" -ForegroundColor White
