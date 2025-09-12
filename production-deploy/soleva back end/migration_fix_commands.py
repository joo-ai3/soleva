#!/usr/bin/env python
"""
Direct Migration Fix Commands for Soleva Django Project

This script provides step-by-step commands to fix the migration dependency issue.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soleva_backend.settings')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)


def show_migration_status():
    """Show current migration status"""
    print("\n📊 Current Migration Status:")
    print("=" * 50)

    os.system("python manage.py showmigrations")


def fix_migration_order():
    """Fix migration order by running them step by step"""
    print("\n🔧 Fixing Migration Order:")
    print("=" * 50)

    commands = [
        ("Run Django built-in migrations first", "python manage.py migrate auth"),
        ("Run content types", "python manage.py migrate contenttypes"),
        ("Run sessions", "python manage.py migrate sessions"),
        ("Run users migration (custom user model)", "python manage.py migrate users"),
        ("Run admin (depends on users)", "python manage.py migrate admin"),
        ("Run shipping (independent)", "python manage.py migrate shipping"),
        ("Run OTP (independent)", "python manage.py migrate otp"),
        ("Run products", "python manage.py migrate products"),
        ("Run offers (depends on users & products)", "python manage.py migrate offers"),
        ("Run cart (depends on users)", "python manage.py migrate cart"),
        ("Run coupons (depends on users)", "python manage.py migrate coupons"),
        ("Run notifications", "python manage.py migrate notifications"),
        ("Run accounting", "python manage.py migrate accounting"),
        ("Run payments", "python manage.py migrate payments"),
        ("Run tracking", "python manage.py migrate tracking"),
        ("Run website management", "python manage.py migrate website_management"),
        ("Run orders (depends on users)", "python manage.py migrate orders"),
    ]

    for description, command in commands:
        print(f"\n▶️  {description}")
        print(f"   Command: {command}")
        result = os.system(command)
        if result == 0:
            print("   ✅ SUCCESS"        else:
            print(f"   ❌ FAILED (exit code: {result})")
            return False

    return True


def alternative_fix():
    """Alternative fix using fake migrations"""
    print("\n🔄 Alternative Fix (if step-by-step fails):")
    print("=" * 50)

    print("This approach resets and fakes the problematic migrations:")
    print()

    fake_commands = [
        "# Reset to clean state",
        "python manage.py migrate --fake-initial",
        "python manage.py migrate auth zero",
        "python manage.py migrate admin zero",
        "python manage.py migrate sessions zero",
        "python manage.py migrate contenttypes zero",
        "",
        "# Run in correct order",
        "python manage.py migrate auth",
        "python manage.py migrate contenttypes",
        "python manage.py migrate sessions",
        "python manage.py migrate users",
        "python manage.py migrate admin",
        "# ... continue with other apps",
    ]

    for cmd in fake_commands:
        if cmd.startswith("#"):
            print(f"\n{cmd}")
        elif cmd.startswith("python"):
            print(f"▶️  {cmd}")
        else:
            print(cmd)


def create_bash_script():
    """Create a bash script for easy execution"""
    script_content = '''#!/bin/bash
# Soleva Migration Fix Script
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
'''

    script_path = BASE_DIR / 'fix_migrations.sh'
    with open(script_path, 'w', newline='\n') as f:
        f.write(script_content)

    # Make executable on Unix-like systems
    try:
        os.chmod(script_path, 0o755)
    except:
        pass  # Skip on Windows

    print(f"\n📄 Created bash script: {script_path}")
    print("Run: ./fix_migrations.sh")


def main():
    """Main function"""
    print("🔧 Soleva Django Migration Fix Tool")
    print("=" * 60)

    show_migration_status()

    print("\n" + "=" * 60)
    print("🎯 SOLUTION OPTIONS:")
    print("=" * 60)

    print("\n1️⃣ RECOMMENDED: Step-by-step migration fix")
    response = input("Run step-by-step migration fix? (y/n): ").lower().strip()

    if response == 'y':
        success = fix_migration_order()
        if success:
            print("\n🎉 Migration fix completed successfully!")
        else:
            print("\n⚠️  Step-by-step fix encountered issues.")
            alternative_fix()
    else:
        print("\n📋 Manual steps:")
        alternative_fix()

    create_bash_script()

    print("\n" + "=" * 60)
    print("📞 SUPPORT:")
    print("If you encounter issues, try the alternative fix above.")
    print("Make sure your database credentials are correct in .env file.")


if __name__ == '__main__':
    main()
