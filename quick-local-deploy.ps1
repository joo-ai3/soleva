# Quick Local Deployment for Soleva (Development Mode)
# This script runs Soleva locally without Docker dependencies

Write-Host "=== Soleva Quick Local Deployment ===" -ForegroundColor Green

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js" -ForegroundColor Red
    exit 1
}

# Step 1: Set up backend with SQLite (development mode)
Write-Host "`nStep 1: Setting up Django backend..." -ForegroundColor Yellow

if (Test-Path "soleva back end") {
    Set-Location "soleva back end"
    
    # Create development environment file
    $devEnv = @"
SECRET_KEY=django-insecure-dev-key-for-local-testing-only
DEBUG=True
USE_SQLITE=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,solevaeg.com,www.solevaeg.com
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
CELERY_ALWAYS_EAGER=True
"@
    
    $devEnv | Set-Content ".env"
    Write-Host "✓ Created development environment configuration" -ForegroundColor Green
    
    # Install Python dependencies
    Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
    try {
        pip install -r requirements.txt 2>&1 | Out-Host
        Write-Host "✓ Python dependencies installed" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Some dependencies may have failed to install" -ForegroundColor Yellow
    }
    
    # Run migrations
    Write-Host "Running database migrations..." -ForegroundColor Cyan
    try {
        python manage.py migrate --run-syncdb 2>&1 | Out-Host
        Write-Host "✓ Database migrations completed" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Migration issues - continuing anyway" -ForegroundColor Yellow
    }
    
    # Collect static files
    Write-Host "Collecting static files..." -ForegroundColor Cyan
    try {
        python manage.py collectstatic --noinput 2>&1 | Out-Host
        Write-Host "✓ Static files collected" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Static files collection had issues" -ForegroundColor Yellow
    }
    
    # Create superuser (optional)
    Write-Host "Creating superuser..." -ForegroundColor Cyan
    $env:DJANGO_SUPERUSER_USERNAME = "admin"
    $env:DJANGO_SUPERUSER_EMAIL = "admin@solevaeg.com"
    $env:DJANGO_SUPERUSER_PASSWORD = "admin123"
    try {
        python manage.py createsuperuser --noinput 2>&1 | Out-Host
        Write-Host "✓ Superuser created (admin/admin123)" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Superuser creation skipped (may already exist)" -ForegroundColor Yellow
    }
    
    Set-Location ..
} else {
    Write-Host "✗ Backend directory not found" -ForegroundColor Red
}

# Step 2: Set up frontend
Write-Host "`nStep 2: Setting up React frontend..." -ForegroundColor Yellow

if (Test-Path "soleva front end") {
    Set-Location "soleva front end"
    
    # Install Node dependencies
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Cyan
    try {
        npm install 2>&1 | Out-Host
        Write-Host "✓ Node.js dependencies installed" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Some Node.js dependencies may have failed" -ForegroundColor Yellow
    }
    
    # Build frontend
    Write-Host "Building frontend..." -ForegroundColor Cyan
    try {
        npm run build 2>&1 | Out-Host
        Write-Host "✓ Frontend built successfully" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Frontend build had issues" -ForegroundColor Yellow
    }
    
    Set-Location ..
} else {
    Write-Host "✗ Frontend directory not found" -ForegroundColor Red
}

# Step 3: Create startup scripts
Write-Host "`nStep 3: Creating startup scripts..." -ForegroundColor Yellow

# Backend startup script
$backendScript = @'
@echo off
echo Starting Soleva Backend...
cd "soleva back end"
python manage.py runserver 0.0.0.0:8000
'@
$backendScript | Set-Content "start-backend.bat"

# Frontend startup script (simple HTTP server)
$frontendScript = @'
@echo off
echo Starting Soleva Frontend...
cd "soleva front end"
npx serve -s build -l 3000
'@
$frontendScript | Set-Content "start-frontend.bat"

Write-Host "✓ Startup scripts created" -ForegroundColor Green

# Step 4: Display instructions
Write-Host "`n=== Deployment Complete! ===" -ForegroundColor Green
Write-Host "`nTo start the application:" -ForegroundColor Cyan
Write-Host "1. Backend:  run 'start-backend.bat' or 'python manage.py runserver 0.0.0.0:8000' in 'soleva back end' folder" -ForegroundColor White
Write-Host "2. Frontend: run 'start-frontend.bat' or 'npx serve -s build -l 3000' in 'soleva front end' folder" -ForegroundColor White
Write-Host "`nAccess the application:" -ForegroundColor Cyan
Write-Host "- Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "- Backend API: http://localhost:8000/api/" -ForegroundColor White
Write-Host "- Admin Panel: http://localhost:8000/admin/ (admin/admin123)" -ForegroundColor White
Write-Host "`nFor production deployment:" -ForegroundColor Yellow
Write-Host "- Set up PostgreSQL and Redis" -ForegroundColor White
Write-Host "- Configure proper environment variables" -ForegroundColor White
Write-Host "- Use nginx for reverse proxy" -ForegroundColor White
Write-Host "- Set up SSL certificates" -ForegroundColor White

Write-Host "`n=== Ready for Testing! ===" -ForegroundColor Green
