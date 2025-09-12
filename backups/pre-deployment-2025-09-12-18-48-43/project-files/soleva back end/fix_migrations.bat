@echo off
REM Soleva Migration Fix Script for Windows
REM Run this script to fix the "relation users does not exist" error

echo 🔧 Fixing Django Migration Dependencies
echo =========================================

echo Step 1: Running Django built-in migrations...
python manage.py migrate auth
if %errorlevel% neq 0 (
    echo ❌ Failed to migrate auth
    pause
    exit /b 1
)

python manage.py migrate contenttypes
if %errorlevel% neq 0 (
    echo ❌ Failed to migrate contenttypes
    pause
    exit /b 1
)

python manage.py migrate sessions
if %errorlevel% neq 0 (
    echo ❌ Failed to migrate sessions
    pause
    exit /b 1
)

echo Step 2: Running custom user model...
python manage.py migrate users
if %errorlevel% neq 0 (
    echo ❌ Failed to migrate users
    pause
    exit /b 1
)

echo Step 3: Running admin ^(depends on users^)...
python manage.py migrate admin
if %errorlevel% neq 0 (
    echo ❌ Failed to migrate admin
    pause
    exit /b 1
)

echo Step 4: Running independent apps...
python manage.py migrate shipping
python manage.py migrate otp

echo Step 5: Running apps that depend on users...
python manage.py migrate products
python manage.py migrate offers
python manage.py migrate cart
python manage.py migrate coupons
python manage.py migrate notifications
python manage.py migrate accounting
python manage.py migrate payments
python manage.py migrate tracking
python manage.py migrate website_management
python manage.py migrate orders

echo ✅ All migrations completed successfully!
echo ===========================================
pause
