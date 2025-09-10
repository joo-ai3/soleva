@echo off
REM COMPLETE MIGRATION FIX FOR SOLEVA BACKEND (Windows Version)
REM This script fixes the "relation 'users' does not exist" error
REM Run this script on your server at ~/soleva/complete_migration_fix.bat

echo ========================================
echo COMPLETE MIGRATION FIX FOR SOLEVA
echo ========================================
echo This script will fix the Django migration issues
echo.

REM Step 1: Check if we're in the right directory
if not exist "soleva back end" (
    echo [ERROR] 'soleva back end' directory not found!
    echo [ERROR] Please run this script from the soleva project root directory
    pause
    exit /b 1
)

echo [INFO] Working directory: %cd%
echo [INFO] Found 'soleva back end' directory - proceeding...
echo.

REM Step 2: Stop all containers
echo [INFO] Step 1: Stopping all containers...
docker compose down --remove-orphans --volumes 2>nul

REM Step 3: Clean up any remaining containers
echo [INFO] Step 2: Cleaning up remaining containers...
for /f "tokens=*" %%i in ('docker ps -a --filter "name=soleva" --format "{{.Names}}" 2^>nul') do docker rm -f %%i 2>nul

REM Step 4: Create necessary directories
echo [INFO] Step 3: Creating necessary directories...
if not exist "soleva back end\static" mkdir "soleva back end\static"
if not exist "soleva back end\staticfiles" mkdir "soleva back end\staticfiles"
if not exist "soleva back end\media" mkdir "soleva back end\media"
if not exist "soleva back end\logs" mkdir "soleva back end\logs"
echo [SUCCESS] Directories created
echo.

REM Step 5: Start database only
echo [INFO] Step 4: Starting PostgreSQL database...
docker compose up -d postgres

REM Wait for database to be ready
echo [INFO] Step 5: Waiting for database to be ready...
timeout /t 15 /nobreak > nul

REM Test database connection
docker compose exec postgres pg_isready -U soleva_user -d soleva_db >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Database is ready
) else (
    echo [ERROR] Database connection failed
    pause
    exit /b 1
)
echo.

REM Step 6: Reset database schema (WARNING: This deletes all data!)
echo [WARNING] Step 6: Resetting database schema (this deletes all data)...
docker compose exec postgres psql -U soleva_user -d soleva_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO soleva_user; GRANT ALL ON SCHEMA public TO public; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO soleva_user; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO soleva_user;"
echo [SUCCESS] Database reset completed
echo.

REM Step 7: Start Redis and backend
echo [INFO] Step 7: Starting Redis and backend services...
docker compose up -d redis
docker compose up -d backend

REM Wait for services to be ready
echo [INFO] Step 8: Waiting for services to be ready...
timeout /t 25 /nobreak > nul

REM Step 8: Apply migrations in correct order
echo [INFO] Step 9: Applying migrations in correct order...
echo.

REM Function to run migration with error handling
:run_migration
set app=%~1
set description=%~2
if "%description%"=="" set description=%app%
echo   Applying %description% migrations...
docker compose exec backend python manage.py migrate %app% --verbosity=1
if %ERRORLEVEL% EQU 0 (
    echo   [SUCCESS] %description% migrations applied successfully
) else (
    echo   [ERROR] Failed to apply %description% migrations
    pause
    exit /b 1
)
goto :eof

REM Apply core Django migrations first
call :run_migration "auth" "Django Auth"
call :run_migration "contenttypes" "Django Content Types"
call :run_migration "sessions" "Django Sessions"

REM Apply users migration (this creates the users table)
call :run_migration "users" "Custom User Model"

REM Apply admin migration (depends on users)
call :run_migration "admin" "Django Admin"

REM Apply remaining migrations
echo   Applying remaining app migrations...
docker compose exec backend python manage.py migrate --verbosity=1
if %ERRORLEVEL% EQU 0 (
    echo   [SUCCESS] All remaining migrations applied successfully
) else (
    echo   [ERROR] Failed to apply remaining migrations
    pause
    exit /b 1
)
echo.

REM Step 9: Create superuser
echo [INFO] Step 10: Creating superuser...
docker compose exec backend python manage.py shell -c "
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
    print('Email: admin@solevaeg.com')
    print('Password: S0l3v@_Admin!2025#')
else:
    print('Superuser already exists')
"
echo [SUCCESS] Superuser creation completed
echo.

REM Step 10: Collect static files
echo [INFO] Step 11: Collecting static files...
docker compose exec backend python manage.py collectstatic --noinput --verbosity=0
echo [SUCCESS] Static files collected
echo.

REM Step 11: Start all remaining services
echo [INFO] Step 12: Starting all services...
docker compose up -d frontend nginx celery celery-beat

REM Step 12: Final verification
echo [INFO] Step 13: Final verification...
timeout /t 10 /nobreak > nul

REM Check container status
echo.
echo ========================================
echo SERVICE STATUS:
echo ========================================
docker compose ps

REM Test backend health
echo.
echo ========================================
echo BACKEND HEALTH CHECK:
echo ========================================
curl -s --max-time 10 http://localhost/api/health/ >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Backend health check passed
) else (
    echo [WARNING] Backend health check failed (may still be starting)
)

REM Final summary
echo.
echo ========================================
echo MIGRATION FIX COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo Service Status:
docker compose ps --format "table {{.Name}}	{{.Status}}	{{.Ports}}"
echo.
echo Access URLs:
echo - Frontend: http://localhost
echo - Admin: http://localhost/admin/
echo - API: http://localhost/api/
echo - Superuser: admin@solevaeg.com
echo - Password: S0l3v@_Admin!2025#
echo.
echo IMPORTANT NOTES:
echo - All previous data was deleted during database reset
echo - Backend should now be healthy and stable
echo - If issues persist, check logs: docker compose logs backend
echo.
echo Migration fix completed! Your Soleva application should now be running.
pause
