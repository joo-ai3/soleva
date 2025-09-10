#!/bin/bash

# =======================================
# Soleva Environment Setup Script
# =======================================
# This script creates a .env file with all necessary environment variables
# for local development

cat > .env << 'EOF'
# =======================================
# Soleva Development Environment Configuration
# =======================================
# This file contains all environment variables needed for local development
# DO NOT commit this file to version control - it contains sensitive information

# =======================================
# Domain Configuration
# =======================================
DOMAIN=localhost
SSL_EMAIL=admin@localhost

# =======================================
# Django Backend Configuration
# =======================================
SECRET_KEY=dev-django-secret-key-for-local-development-min-50-chars-recommended-12345
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,*

# =======================================
# Database Configuration (PostgreSQL)
# =======================================
DB_NAME=soleva_db
DB_USER=soleva_user
DB_PASSWORD=Soleva@2025
DB_HOST=postgres
DB_PORT=5432

# =======================================
# Redis Configuration
# =======================================
REDIS_PASSWORD=Redis@2025

# =======================================
# Email Configuration (Console backend for development)
# =======================================
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@localhost
EMAIL_HOST_PASSWORD=dev-email-password
DEFAULT_FROM_EMAIL=noreply@localhost

# =======================================
# Payment Gateway Configuration (Development placeholders)
# =======================================
PAYMOB_API_KEY=dev-paymob-api-key
PAYMOB_SECRET_KEY=dev-paymob-secret-key
STRIPE_PUBLISHABLE_KEY=pk_test_dev-stripe-publishable-key
STRIPE_SECRET_KEY=sk_test_dev-stripe-secret-key

# =======================================
# Analytics & Tracking (Development placeholders)
# =======================================
FACEBOOK_PIXEL_ID=dev-facebook-pixel-id
GOOGLE_ANALYTICS_ID=G-DEVXXXXXXXXX
TIKTOK_PIXEL_ID=dev-tiktok-pixel-id
SNAPCHAT_PIXEL_ID=dev-snapchat-pixel-id

# =======================================
# Admin Configuration
# =======================================
ADMIN_PASSWORD=S0l3v@_Admin!2025#

# =======================================
# Security (Development keys)
# =======================================
JWT_SECRET_KEY=dev-jwt-secret-key-for-local-development-only
CSRF_SECRET_KEY=dev-csrf-secret-key-for-local-development-only

# =======================================
# Backup Configuration (Optional)
# =======================================
BACKUP_SCHEDULE="0 2 * * *"
BACKUP_RETENTION_DAYS=30

# =======================================
# Monitoring (Optional - disabled for development)
# =======================================
SENTRY_DSN=
SLACK_WEBHOOK_URL=
EOF

echo "✅ .env file created successfully!"
echo "📁 Environment file location: $(pwd)/.env"
echo "🔒 Make sure .env is in your .gitignore file"
echo ""
echo "🚀 To start the services, run:"
echo "   docker compose up -d"
echo ""
echo "📊 To check service status:"
echo "   docker compose ps"
echo ""
echo "🔍 To view logs:"
echo "   docker compose logs -f [service-name]"
echo ""
echo "🛑 To stop services:"
echo "   docker compose down"
