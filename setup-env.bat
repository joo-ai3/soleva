@echo off
REM =======================================
REM Soleva Environment Setup Script (Windows)
REM =======================================
REM This script creates a .env file with all necessary environment variables
REM for local development

echo.
echo ========================================
echo 🧪 Creating .env file...
echo ========================================
echo.

REM Create the .env file with proper content
(
echo # =======================================
echo # Soleva Development Environment Configuration
echo # =======================================
echo # This file contains all environment variables needed for local development
echo # DO NOT commit this file to version control - it contains sensitive information
echo.
echo # =======================================
echo # Domain Configuration
echo # =======================================
echo DOMAIN=localhost
echo SSL_EMAIL=admin@localhost
echo.
echo # =======================================
echo # Django Backend Configuration
echo # =======================================
echo SECRET_KEY=dev-django-secret-key-for-local-development-min-50-chars-recommended-12345
echo DEBUG=True
echo ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,*
echo.
echo # =======================================
echo # Database Configuration (PostgreSQL)
echo # =======================================
echo DB_NAME=soleva_db
echo DB_USER=soleva_user
echo DB_PASSWORD=Soleva@2025
echo DB_HOST=postgres
echo DB_PORT=5432
echo.
echo # =======================================
echo # Redis Configuration
echo # =======================================
echo REDIS_PASSWORD=Redis@2025
echo.
echo # =======================================
echo # Email Configuration (Console backend for development)
echo # =======================================
echo EMAIL_HOST=smtp.gmail.com
echo EMAIL_PORT=587
echo EMAIL_USE_TLS=True
echo EMAIL_HOST_USER=noreply@localhost
echo EMAIL_HOST_PASSWORD=dev-email-password
echo DEFAULT_FROM_EMAIL=noreply@localhost
echo.
echo # =======================================
echo # Payment Gateway Configuration (Development placeholders)
echo # =======================================
echo PAYMOB_API_KEY=dev-paymob-api-key
echo PAYMOB_SECRET_KEY=dev-paymob-secret-key
echo STRIPE_PUBLISHABLE_KEY=pk_test_dev-stripe-publishable-key
echo STRIPE_SECRET_KEY=sk_test_dev-stripe-secret-key
echo.
echo # =======================================
echo # Analytics ^& Tracking (Development placeholders)
echo # =======================================
echo FACEBOOK_PIXEL_ID=dev-facebook-pixel-id
echo GOOGLE_ANALYTICS_ID=G-DEVXXXXXXXXX
echo TIKTOK_PIXEL_ID=dev-tiktok-pixel-id
echo SNAPCHAT_PIXEL_ID=dev-snapchat-pixel-id
echo.
echo # =======================================
echo # Admin Configuration
echo # =======================================
echo ADMIN_PASSWORD=?3aeeSjqq
echo.
echo # =======================================
echo # Security (Development keys)
echo # =======================================
echo JWT_SECRET_KEY=dev-jwt-secret-key-for-local-development-only
echo CSRF_SECRET_KEY=dev-csrf-secret-key-for-local-development-only
echo.
echo # =======================================
echo # Backup Configuration (Optional)
echo # =======================================
echo BACKUP_SCHEDULE="0 2 * * *"
echo BACKUP_RETENTION_DAYS=30
echo.
echo # =======================================
echo # Monitoring (Optional - disabled for development)
echo # =======================================
echo SENTRY_DSN=
echo SLACK_WEBHOOK_URL=
) > .env

if exist ".env" (
    echo.
    echo ========================================
    echo ✅ .env file created successfully!
    echo ========================================
    echo.
    echo 📁 Environment file location: %cd%\.env
    echo 🔒 Make sure .env is in your .gitignore file
    echo.
    echo 🚀 To start the services, run:
    echo    docker compose up -d
    echo.
    echo 📊 To check service status:
    echo    docker compose ps
    echo.
    echo 🔍 To view logs:
    echo    docker compose logs -f [service-name]
    echo.
    echo 🛑 To stop services:
    echo    docker compose down
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ Failed to create .env file
    echo ========================================
    echo.
    echo Please check file permissions and try again.
    echo.
)

echo Press any key to continue...
pause > nul
