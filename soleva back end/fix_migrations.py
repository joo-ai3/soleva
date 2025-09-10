#!/usr/bin/env python
"""
Migration Fix Script for Soleva Django Project

This script helps resolve migration dependency issues with custom user models.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soleva_backend.settings')

django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.apps import apps


def check_migration_status():
    """Check the current migration status"""
    print("=== Current Migration Status ===")
    with connection.cursor() as cursor:
        # Get applied migrations
        cursor.execute("""
            SELECT app, name, applied
            FROM django_migrations
            ORDER BY app, applied ASC
        """)
        migrations = cursor.fetchall()

        if migrations:
            for app, name, applied in migrations:
                status = "✓" if applied else "✗"
                print("25")
        else:
            print("No migrations applied yet.")


def fix_migration_dependencies():
    """Fix migration dependency issues"""
    print("\n=== Fixing Migration Dependencies ===")

    # First, ensure users app migrations run before others
    print("1. Ensuring users migrations run first...")

    # List of apps that depend on users
    dependent_apps = [
        'offers', 'orders', 'cart', 'coupons', 'notifications',
        'payments', 'tracking', 'website_management'
    ]

    for app_name in dependent_apps:
        try:
            app_config = apps.get_app_config(app_name)
            migrations_dir = Path(app_config.path) / 'migrations'

            if migrations_dir.exists():
                migration_files = list(migrations_dir.glob('*.py'))
                if migration_files:
                    print(f"   Found migrations for {app_name}: {len(migration_files)} files")
                    for migration_file in sorted(migration_files):
                        if migration_file.name != '__init__.py':
                            print(f"     - {migration_file.name}")
        except Exception as e:
            print(f"   Warning: Could not check {app_name}: {e}")


def create_migration_order_script():
    """Create a script to run migrations in correct order"""
    print("\n=== Creating Migration Order Script ===")

    script_content = '''#!/bin/bash
# Migration Order Script for Soleva Django Project
# This script runs migrations in the correct order to avoid dependency issues

set -e

echo "=== Running Migrations in Correct Order ==="

# Step 1: Run Django built-in migrations first
echo "1. Running Django built-in migrations..."
python manage.py migrate auth
python manage.py migrate contenttypes
python manage.py migrate sessions

# Step 2: Run custom user model migration
echo "2. Running users app migration..."
python manage.py migrate users

# Step 3: Run admin after users (since admin references users)
echo "3. Running admin app migration..."
python manage.py migrate admin

# Step 4: Run remaining apps in order
echo "4. Running remaining app migrations..."

# Apps that don't depend on users
python manage.py migrate shipping
python manage.py migrate otp

# Apps that depend on users (run after users migration)
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

echo "=== All migrations completed successfully! ==="
'''

    script_path = BASE_DIR / 'run_migrations_ordered.sh'
    with open(script_path, 'w', newline='\n') as f:
        f.write(script_content)

    # Make script executable
    os.chmod(script_path, 0o755)

    print(f"Created migration order script: {script_path}")
    print("Run this script instead of 'python manage.py migrate'")


def manual_migration_steps():
    """Provide manual steps for fixing migrations"""
    print("\n=== Manual Migration Steps ===")
    print("If the automated script doesn't work, follow these steps:")
    print()
    print("1. Reset migrations (CAUTION: This will delete existing data):")
    print("   python manage.py migrate --fake-initial")
    print("   python manage.py migrate auth zero")
    print("   python manage.py migrate admin zero")
    print("   python manage.py migrate sessions zero")
    print("   python manage.py migrate contenttypes zero")
    print()
    print("2. Run migrations in correct order:")
    print("   python manage.py migrate auth")
    print("   python manage.py migrate contenttypes")
    print("   python manage.py migrate sessions")
    print("   python manage.py migrate users")
    print("   python manage.py migrate admin")
    print("   python manage.py migrate shipping")
    print("   python manage.py migrate otp")
    print("   python manage.py migrate products")
    print("   python manage.py migrate offers")
    print("   python manage.py migrate cart")
    print("   python manage.py migrate coupons")
    print("   python manage.py migrate notifications")
    print("   python manage.py migrate accounting")
    print("   python manage.py migrate payments")
    print("   python manage.py migrate tracking")
    print("   python manage.py migrate website_management")
    print("   python manage.py migrate orders")


def main():
    """Main function"""
    print("🔧 Soleva Django Migration Fix Tool")
    print("=" * 50)

    check_migration_status()
    fix_migration_dependencies()
    create_migration_order_script()
    manual_migration_steps()

    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print("1. Use the generated script: ./run_migrations_ordered.sh")
    print("2. Or follow the manual steps above")
    print("3. This will ensure proper migration order and fix the 'relation users does not exist' error")


if __name__ == '__main__':
    main()
