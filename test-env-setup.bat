@echo off
REM =======================================
REM Soleva Environment Test Script (Windows)
REM =======================================
REM This script tests if the environment is properly configured

echo.
echo ========================================
echo 🧪 Testing Soleva Environment Setup...
echo ========================================
echo.

REM Check if .env file exists
echo 📁 Checking .env file...
if exist ".env" (
    echo ✅ .env file exists
) else (
    echo ❌ .env file missing - run setup-env.bat first
    goto :error
)

REM Check if .env is in .gitignore
echo 🔒 Checking .gitignore security...
findstr /B /C:".env" .gitignore >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ .env is properly ignored in .gitignore
) else (
    echo ❌ .env is NOT in .gitignore - add it for security!
)

REM Check if docker-compose.yml exists
echo 🐳 Checking docker-compose.yml...
if exist "docker-compose.yml" (
    echo ✅ docker-compose.yml exists
) else (
    echo ❌ docker-compose.yml missing
    goto :error
)

REM Check Docker availability
echo 🐳 Checking Docker...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker is installed
) else (
    echo ❌ Docker is not installed
    goto :error
)

REM Check Docker Compose availability
echo 🐳 Checking Docker Compose...
docker compose version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker Compose is available
    goto :success
)

docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker Compose is available
) else (
    echo ❌ Docker Compose is not available
    goto :error
)

:success
echo.
echo ========================================
echo 📊 Environment Summary:
echo ========================================
echo Database: PostgreSQL (soleva_db)
echo Redis: Enabled with authentication
echo Backend: Django (DEBUG=True)
echo Domain: localhost
echo.
echo 🚀 Ready to start services!
echo ========================================
echo.
echo Run: docker compose up -d
echo.
echo Check status: docker compose ps
echo.
echo View logs: docker compose logs -f
echo.
echo Stop services: docker compose down
echo.
goto :end

:error
echo.
echo ❌ Environment setup has issues. Please fix them before proceeding.
echo.
goto :end

:end
echo.
pause
