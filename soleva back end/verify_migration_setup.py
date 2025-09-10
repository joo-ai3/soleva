#!/usr/bin/env python
"""
Verify Migration Setup for Soleva Project
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

from django.conf import settings
from django.apps import apps


def verify_user_model():
    """Verify User model configuration"""
    print("\n👤 VERIFYING USER MODEL CONFIGURATION")
    print("=" * 50)

    # Check AUTH_USER_MODEL
    auth_user_model = getattr(settings, 'AUTH_USER_MODEL', None)
    print(f"AUTH_USER_MODEL: {auth_user_model}")

    if auth_user_model == 'users.User':
        print("✅ AUTH_USER_MODEL is correctly set")
    else:
        print(f"❌ AUTH_USER_MODEL should be 'users.User', but is '{auth_user_model}'")

    # Check if User model exists
    try:
        from users.models import User
        print("✅ User model imported successfully")
        print(f"   User model: {User.__name__}")
        print(f"   Database table: {User._meta.db_table}")
        print(f"   USERNAME_FIELD: {User.USERNAME_FIELD}")
        print(f"   REQUIRED_FIELDS: {User.REQUIRED_FIELDS}")
    except ImportError as e:
        print(f"❌ Failed to import User model: {e}")
        return False

    return True


def verify_installed_apps():
    """Verify INSTALLED_APPS configuration"""
    print("\n📦 VERIFYING INSTALLED_APPS")
    print("=" * 50)

    installed_apps = getattr(settings, 'INSTALLED_APPS', [])
    required_apps = ['users', 'django.contrib.auth', 'django.contrib.admin']

    for app in required_apps:
        if app in installed_apps:
            print(f"✅ {app} is in INSTALLED_APPS")
        else:
            print(f"❌ {app} is missing from INSTALLED_APPS")

    print(f"\nTotal apps in INSTALLED_APPS: {len(installed_apps)}")
    return all(app in installed_apps for app in required_apps)


def verify_migration_files():
    """Verify migration files exist"""
    print("\n📁 VERIFYING MIGRATION FILES")
    print("=" * 50)

    apps_to_check = ['users', 'auth', 'admin', 'contenttypes', 'sessions']
    migration_issues = []

    for app_name in apps_to_check:
        try:
            app_config = apps.get_app_config(app_name)
            migrations_dir = Path(app_config.path) / 'migrations'

            if migrations_dir.exists():
                migration_files = [f for f in migrations_dir.glob('*.py') if f.name != '__init__.py']
                print(f"✅ {app_name}: {len(migration_files)} migration files found")
            else:
                print(f"⚠️  {app_name}: No migrations directory found")
                migration_issues.append(app_name)

        except Exception as e:
            print(f"❌ {app_name}: Error checking migrations - {e}")
            migration_issues.append(app_name)

    return len(migration_issues) == 0, migration_issues


def check_database_configuration():
    """Check database configuration"""
    print("\n🗄️  VERIFYING DATABASE CONFIGURATION")
    print("=" * 50)

    databases = getattr(settings, 'DATABASES', {})
    default_db = databases.get('default', {})

    db_engine = default_db.get('ENGINE', '')
    db_name = default_db.get('NAME', '')
    db_host = default_db.get('HOST', 'localhost')

    print(f"Database Engine: {db_engine}")
    print(f"Database Name: {db_name}")
    print(f"Database Host: {db_host}")

    if 'postgresql' in db_engine:
        print("✅ PostgreSQL configuration detected")
        if db_host == 'postgres':
            print("✅ Docker container hostname detected")
        elif db_host in ['localhost', '127.0.0.1']:
            print("⚠️  Local PostgreSQL detected - ensure it's running")
    elif 'sqlite3' in db_engine:
        print("ℹ️  SQLite configuration detected")
    else:
        print(f"⚠️  Unknown database engine: {db_engine}")

    return True


def provide_recommendations():
    """Provide recommendations based on findings"""
    print("\n💡 RECOMMENDATIONS")
    print("=" * 50)

    recommendations = [
        "1. Run migrations in this order:",
        "   python manage.py migrate auth",
        "   python manage.py migrate contenttypes",
        "   python manage.py migrate sessions",
        "   python manage.py migrate users",
        "   python manage.py migrate admin",
        "   # ... then other apps",
        "",
        "2. If using Docker:",
        "   docker compose run --rm backend python manage.py migrate users",
        "   docker compose run --rm backend python manage.py migrate admin",
        "",
        "3. For production deployment:",
        "   Ensure PostgreSQL is running before applying migrations",
        "   Use the migration_fix_final.sh script",
        "",
        "4. To reset if needed:",
        "   python manage.py migrate --fake-initial",
        "   python manage.py migrate auth zero",
        "   python manage.py migrate admin zero",
        "   python manage.py migrate users zero"
    ]

    for rec in recommendations:
        print(rec)


def main():
    """Main verification function"""
    print("🔍 SOLEVA MIGRATION SETUP VERIFICATION")
    print("=" * 60)

    all_good = True

    # Run all checks
    user_model_ok = verify_user_model()
    apps_ok = verify_installed_apps()
    migrations_ok, migration_issues = verify_migration_files()
    db_ok = check_database_configuration()

    all_good = user_model_ok and apps_ok and migrations_ok and db_ok

    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)

    checks = [
        ("User Model Configuration", user_model_ok),
        ("INSTALLED_APPS", apps_ok),
        ("Migration Files", migrations_ok),
        ("Database Configuration", db_ok),
    ]

    for check_name, status in checks:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check_name}: {'PASS' if status else 'FAIL'}")

    if migration_issues:
        print(f"\n⚠️  Migration issues found for: {', '.join(migration_issues)}")

    if all_good:
        print("\n🎉 ALL CHECKS PASSED!")
        print("Your Django setup looks good for migrations.")
    else:
        print("\n⚠️  SOME CHECKS FAILED!")
        print("Please address the issues above before running migrations.")

    provide_recommendations()


if __name__ == '__main__':
    main()
