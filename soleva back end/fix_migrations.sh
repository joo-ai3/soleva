#!/bin/bash
# Soleva Migration Fix Script for Linux/Unix
# Run this script to fix the "relation users does not exist" error

set -e

echo "🔧 Fixing Django Migration Dependencies"
echo "========================================"

echo "Step 1: Running Django built-in migrations..."
python manage.py migrate auth
python manage.py migrate contenttypes
python manage.py migrate sessions

echo "Step 2: Running custom user model..."
python manage.py migrate users

echo "Step 3: Running admin (depends on users)..."
python manage.py migrate admin

echo "Step 4: Running independent apps..."
python manage.py migrate shipping
python manage.py migrate otp

echo "Step 5: Running apps that depend on users..."
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

echo "✅ All migrations completed successfully!"
echo "=========================================="
