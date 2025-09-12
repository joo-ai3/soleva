#!/usr/bin/env python
"""
Script to check and fix Django migration order issues
Specifically addresses the 'relation "users" does not exist' error
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soleva_backend.settings')

def check_migration_order():
    """Check the current migration order and dependencies"""
    print("🔍 CHECKING MIGRATION ORDER")
    print("=" * 50)

    try:
        django.setup()

        from django.db import connection
        from django.apps import apps
        from django.contrib.auth import get_user_model

        # Check AUTH_USER_MODEL setting
        from django.conf import settings
        auth_user_model = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
        print(f"✅ AUTH_USER_MODEL: {auth_user_model}")

        # Check if User model can be imported
        try:
            User = get_user_model()
            print(f"✅ User model: {User.__name__}")
            print(f"   App: {User._meta.app_label}")
            print(f"   Table: {User._meta.db_table}")
        except Exception as e:
            print(f"❌ User model error: {e}")
            return False

        # Check INSTALLED_APPS order
        print(f"\n📋 INSTALLED_APPS order:")
        local_apps = ['users', 'products', 'orders', 'cart', 'coupons', 'notifications',
                     'accounting', 'shipping', 'payments', 'tracking', 'offers', 'otp', 'website_management']

        for i, app in enumerate(local_apps, 1):
            if app in settings.INSTALLED_APPS:
                status = "✅" if app == 'users' and i <= 5 else "✅"
                print(f"   {status} {i:2d}. {app}")
            else:
                print(f"   ❌ {i:2d}. {app} (not in INSTALLED_APPS)")

        # Check migration files
        print(f"\n📁 Migration files status:")
        for app in ['users', 'admin', 'auth', 'contenttypes', 'sessions']:
            migration_dir = BASE_DIR / app / 'migrations'
            if migration_dir.exists():
                migration_files = list(migration_dir.glob('*.py'))
                migration_files = [f for f in migration_files if not f.name.startswith('__')]
                count = len(migration_files)
                status = "✅" if count > 0 else "❌"
                print(f"   {status} {app}: {count} migration files")
            else:
                print(f"   ❌ {app}: migration directory not found")

        return True

    except Exception as e:
        print(f"❌ Error checking migration order: {e}")
        return False

def suggest_migration_order():
    """Suggest the correct migration order"""
    print(f"\n💡 RECOMMENDED MIGRATION ORDER:")
    print("=" * 50)
    print("1. python manage.py migrate auth")
    print("2. python manage.py migrate contenttypes")
    print("3. python manage.py migrate sessions")
    print("4. python manage.py migrate users")
    print("5. python manage.py migrate admin")
    print("6. python manage.py migrate [other apps]")
    print("")
    print("This ensures the custom User model is created before")
    print("the admin app tries to reference it.")

def fix_static_dirs():
    """Check and fix static directories"""
    print(f"\n📁 CHECKING STATIC DIRECTORIES:")
    print("=" * 50)

    static_dir = BASE_DIR / 'static'
    staticfiles_dir = BASE_DIR / 'staticfiles'
    media_dir = BASE_DIR / 'media'
    logs_dir = BASE_DIR / 'logs'

    dirs_to_check = [
        ('static', static_dir),
        ('staticfiles', staticfiles_dir),
        ('media', media_dir),
        ('logs', logs_dir)
    ]

    for name, path in dirs_to_check:
        if path.exists():
            print(f"✅ {name}: {path} (exists)")
        else:
            print(f"❌ {name}: {path} (missing)")
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"   📁 Created directory: {path}")
            except Exception as e:
                print(f"   ❌ Failed to create: {e}")

if __name__ == '__main__':
    print("🔧 SOLEVA MIGRATION ORDER CHECKER")
    print("=" * 60)

    success = check_migration_order()
    fix_static_dirs()
    suggest_migration_order()

    print(f"\n" + "=" * 60)
    if success:
        print("✅ Migration setup looks good!")
        print("If you're still getting errors, try:")
        print("1. Delete all migration files (except __init__.py)")
        print("2. Run: python manage.py makemigrations")
        print("3. Run migrations in the order shown above")
    else:
        print("❌ Migration setup has issues!")
        print("Run the fix-migration-issues.sh script to resolve them.")
