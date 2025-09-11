@echo off
echo ========================================
echo DOCKER RESTART SCRIPT FOR SOLEVA
echo ========================================
echo.

REM Stop existing containers
echo [INFO] Stopping existing containers...
docker compose down --remove-orphans 2>nul

REM Wait a moment
timeout /t 5 /nobreak > nul

REM Start containers with the new healthcheck
echo [INFO] Starting containers with updated Nginx healthcheck...
docker compose up -d

REM Wait for services to initialize
echo [INFO] Waiting for services to initialize...
timeout /t 20 /nobreak > nul

REM Check container status
echo.
echo ========================================
echo CONTAINER STATUS:
echo ========================================
docker compose ps

REM Check if Nginx is healthy
echo.
echo ========================================
echo NGINX HEALTH CHECK:
echo ========================================
docker compose exec nginx wget --no-verbose --tries=1 --spider http://backend:8000/api/health/ 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Nginx can successfully reach backend health endpoint
) else (
    echo [WARNING] Nginx health check failed
)

echo.
echo ========================================
echo RESTART COMPLETE
echo ========================================
echo.
echo If Nginx shows as 'healthy', the fix was successful!
echo If it's still 'unhealthy', there may be other issues.
echo.
pause
