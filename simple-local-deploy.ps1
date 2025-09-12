# Simple Local Deployment for Soleva
Write-Host "=== Soleva Simple Local Deployment ===" -ForegroundColor Green

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
python --version
Write-Host "Checking Node.js..." -ForegroundColor Yellow
node --version

# Set up backend
Write-Host "`nSetting up backend..." -ForegroundColor Yellow
if (Test-Path "soleva back end") {
    Set-Location "soleva back end"
    
    # Create simple .env file
    Write-Host "Creating environment file..." -ForegroundColor Cyan
    $env = "SECRET_KEY=dev-key-123
DEBUG=True  
USE_SQLITE=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,solevaeg.com
DATABASE_URL=sqlite:///db.sqlite3"
    
    $env | Set-Content ".env"
    Write-Host "Environment file created" -ForegroundColor Green
    
    # Install dependencies
    Write-Host "Installing Python packages..." -ForegroundColor Cyan
    pip install -r requirements.txt
    
    # Run migrations
    Write-Host "Running migrations..." -ForegroundColor Cyan
    python manage.py migrate
    
    # Create superuser
    Write-Host "Creating superuser..." -ForegroundColor Cyan
    $env:DJANGO_SUPERUSER_USERNAME = "admin"
    $env:DJANGO_SUPERUSER_EMAIL = "admin@solevaeg.com"
    $env:DJANGO_SUPERUSER_PASSWORD = "admin123"
    python manage.py createsuperuser --noinput
    
    Set-Location ..
}

# Set up frontend
Write-Host "`nSetting up frontend..." -ForegroundColor Yellow
if (Test-Path "soleva front end") {
    Set-Location "soleva front end"
    
    Write-Host "Installing Node packages..." -ForegroundColor Cyan
    npm install
    
    Write-Host "Building frontend..." -ForegroundColor Cyan
    npm run build
    
    Set-Location ..
}

Write-Host "`n=== Setup Complete! ===" -ForegroundColor Green
Write-Host "To start services:" -ForegroundColor Cyan
Write-Host "Backend:  cd 'soleva back end' && python manage.py runserver 0.0.0.0:8000" -ForegroundColor White
Write-Host "Frontend: cd 'soleva front end' && npx serve -s build -l 3000" -ForegroundColor White
