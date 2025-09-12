@echo off
echo ========================================
echo       Starting Soleva Platform
echo ========================================

echo.
echo Starting Django Backend...
start "Soleva Backend" cmd /k "cd 'soleva back end' && python manage.py runserver 0.0.0.0:8000"

echo.
echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo Starting React Frontend...
start "Soleva Frontend" cmd /k "cd 'soleva front end' && npx serve -s build -p 3000"

echo.
echo ========================================
echo   Soleva Platform is starting up!
echo ========================================
echo.
echo Services will be available at:
echo   Frontend: http://localhost:3000 (or alternative port)
echo   Backend:  http://localhost:8000
echo   Admin:    http://localhost:8000/admin
echo.
echo Press any key to continue...
pause >nul