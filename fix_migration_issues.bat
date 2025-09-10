@echo off
REM Windows batch script to fix Django migration issues for Soleva
REM This script should be run on the server where Docker is installed

echo ========================================
echo FIXING SOLEVA BACKEND MIGRATION ISSUES
echo ========================================

REM Step 1: Stop all containers
echo Step 1: Stopping all containers...
docker compose down --remove-orphans

REM Step 2: Clean up containers
echo Step 2: Removing orphan containers...
for /f "tokens=*" %%i in ('docker ps -a --filter "name=soleva" --format "{{.Names}}"') do docker rm -f %%i

REM Step 3: Create static directories
echo Step 3: Creating static directories...
if not exist "soleva back end\static" mkdir "soleva back end\static"
if not exist "soleva back end\staticfiles" mkdir "soleva back end\staticfiles"
if not exist "soleva back end\media" mkdir "soleva back end\media"
if not exist "soleva back end\logs" mkdir "soleva back end\logs"

REM Step 4: Start database only
echo Step 4: Starting database...
docker compose up -d postgres
timeout /t 10 /nobreak > nul

REM Step 5: Reset database (CAUTION: This deletes all data!)
echo Step 5: Resetting database...
docker compose exec postgres psql -U soleva_user -d soleva_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO soleva_user; GRANT ALL ON SCHEMA public TO public; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO soleva_user; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO soleva_user;"

REM Step 6: Start backend and Redis
echo Step 6: Starting backend and Redis...
docker compose up -d redis
docker compose up -d backend
timeout /t 20 /nobreak > nul

REM Step 7: Apply migrations in correct order
echo Step 7: Applying migrations in correct order...

REM Apply core Django migrations first
docker compose exec backend python manage.py migrate auth --verbosity=2
docker compose exec backend python manage.py migrate contenttypes --verbosity=2
docker compose exec backend python manage.py migrate sessions --verbosity=2

REM Apply users migration (this creates the users table)
docker compose exec backend python manage.py migrate users --verbosity=2

REM Apply admin migration (now users table exists)
docker compose exec backend python manage.py migrate admin --verbosity=2

REM Apply remaining migrations
docker compose exec backend python manage.py migrate --verbosity=2

REM Step 8: Create superuser
echo Step 8: Creating superuser...
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
else:
    print('Superuser already exists')
"

REM Step 9: Collect static files
echo Step 9: Collecting static files...
docker compose exec backend python manage.py collectstatic --noinput --verbosity=0

REM Step 10: Start all services
echo Step 10: Starting all services...
docker compose up -d frontend nginx celery celery-beat

REM Step 11: Final verification
echo Step 11: Final verification...
timeout /t 5 /nobreak > nul

echo.
echo ========================================
echo MIGRATION ISSUES FIXED!
echo ========================================
echo.
echo Service Status:
docker compose ps

echo.
echo Access URLs:
echo - Frontend: http://localhost
echo - Admin: http://localhost/admin/
echo - API: http://localhost/api/
echo - Superuser: admin@solevaeg.com

echo.
echo IMPORTANT:
echo - All previous data was deleted during database reset
echo - Backend should now be healthy and stable
echo - If issues persist, check logs: docker compose logs backend

pause
