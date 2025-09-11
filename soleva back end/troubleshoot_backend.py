#!/usr/bin/env python
"""
Backend Container Troubleshooting Script
Diagnoses common issues with Django backend startup
"""

import os
import sys
import django
from pathlib import Path
import subprocess

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soleva_backend.settings')

def run_command(cmd, description):
    """Run a command and return the result"""
    print(f"\n🔍 {description}")
    print(f"   Command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ SUCCESS")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        else:
            print("   ❌ FAILED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        return False, "", str(e)

def check_python_environment():
    """Check Python environment"""
    print("\n🐍 PYTHON ENVIRONMENT CHECK")
    print("=" * 50)

    # Check Python version
    success, stdout, stderr = run_command("python --version", "Checking Python version")
    if not success:
        run_command("python3 --version", "Checking Python3 version")

    # Check Django
    success, stdout, stderr = run_command("python -c \"import django; print(f'Django {django.VERSION}')\"", "Checking Django import")

    # Check key packages
    packages_to_check = [
        'gunicorn', 'gevent', 'psycopg2', 'redis', 'celery',
        'rest_framework', 'corsheaders', 'whitenoise'
    ]

    print("\n📦 CHECKING PYTHON PACKAGES")
    for package in packages_to_check:
        success, stdout, stderr = run_command(
            f"python -c \"import {package}; print('{package} available')\"",
            f"Checking {package} availability"
        )

def check_database_connection():
    """Check database connection"""
    print("\n🗄️ DATABASE CONNECTION CHECK")
    print("=" * 50)

    db_host = os.environ.get('DB_HOST', 'postgres')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'soleva_db')
    db_user = os.environ.get('DB_USER', 'soleva_user')

    print(f"Database Host: {db_host}")
    print(f"Database Port: {db_port}")
    print(f"Database Name: {db_name}")
    print(f"Database User: {db_user}")

    # Check if database is reachable
    success, stdout, stderr = run_command(f"nc -z {db_host} {db_port}", "Testing database connectivity")
    if not success:
        print("   ⚠️  Database not reachable - this will cause startup failures")

def check_redis_connection():
    """Check Redis connection"""
    print("\n🔴 REDIS CONNECTION CHECK")
    print("=" * 50)

    # Check if Redis is reachable
    success, stdout, stderr = run_command("nc -z redis 6379", "Testing Redis connectivity")
    if not success:
        print("   ⚠️  Redis not reachable - this will cause startup failures")

def check_django_configuration():
    """Check Django configuration"""
    print("\n⚙️ DJANGO CONFIGURATION CHECK")
    print("=" * 50)

    try:
        django.setup()
        print("✅ Django setup successful")

        from django.conf import settings

        # Check critical settings
        checks = [
            ('SECRET_KEY', bool(settings.SECRET_KEY)),
            ('DEBUG', 'DEBUG setting'),
            ('ALLOWED_HOSTS', len(settings.ALLOWED_HOSTS) > 0),
            ('INSTALLED_APPS', len(settings.INSTALLED_APPS) > 0),
            ('DATABASES', 'default' in settings.DATABASES),
            ('AUTH_USER_MODEL', settings.AUTH_USER_MODEL),
        ]

        for check_name, value in checks:
            if isinstance(value, bool):
                status = "✅" if value else "❌"
                print(f"   {status} {check_name}: {value}")
            else:
                print(f"   ✅ {check_name}: {value}")

        # Check if User model can be imported
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            print(f"   ✅ User model: {User.__name__}")
        except Exception as e:
            print(f"   ❌ User model error: {e}")

    except Exception as e:
        print(f"❌ Django configuration error: {e}")

def check_file_permissions():
    """Check file permissions"""
    print("\n📁 FILE PERMISSIONS CHECK")
    print("=" * 50)

    important_files = [
        'manage.py',
        'soleva_backend/settings.py',
        'soleva_backend/wsgi.py',
        'requirements.txt',
    ]

    for file_path in important_files:
        full_path = BASE_DIR / file_path
        if full_path.exists():
            print(f"   ✅ {file_path} exists")
        else:
            print(f"   ❌ {file_path} missing")

def test_django_commands():
    """Test basic Django commands"""
    print("\n🎯 DJANGO COMMANDS TEST")
    print("=" * 50)

    commands_to_test = [
        ("python manage.py check", "Django system check"),
        ("python manage.py --version", "Django version check"),
    ]

    for cmd, description in commands_to_test:
        success, stdout, stderr = run_command(cmd, description)

def generate_troubleshooting_report():
    """Generate a comprehensive troubleshooting report"""
    print("\n📋 TROUBLESHOOTING REPORT")
    print("=" * 70)

    report = []

    # Check environment variables
    print("\n🔧 ENVIRONMENT VARIABLES")
    critical_env_vars = [
        'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
        'REDIS_PASSWORD', 'SECRET_KEY', 'DEBUG', 'DJANGO_SETTINGS_MODULE'
    ]

    for var in critical_env_vars:
        value = os.environ.get(var, 'NOT SET')
        if var in ['DB_PASSWORD', 'SECRET_KEY', 'REDIS_PASSWORD']:
            display_value = '*' * len(value) if value != 'NOT SET' else value
        else:
            display_value = value

        status = "✅" if value != 'NOT SET' else "❌"
        print(f"   {status} {var}: {display_value}")

    print("\n💡 RECOMMENDATIONS:")
    print("1. Ensure all database and Redis services are running")
    print("2. Check that environment variables are properly set")
    print("3. Verify that all required Python packages are installed")
    print("4. Make sure the database is accessible and credentials are correct")
    print("5. Check file permissions for the application user")
    print("6. Review Django logs for specific error messages")

def main():
    """Main troubleshooting function"""
    print("🔧 SOLEVA BACKEND TROUBLESHOOTING TOOL")
    print("=" * 70)
    print("This tool diagnoses common backend container startup issues")

    # Run all diagnostic checks
    check_python_environment()
    check_database_connection()
    check_redis_connection()
    check_django_configuration()
    check_file_permissions()
    test_django_commands()
    generate_troubleshooting_report()

    print("\n" + "=" * 70)
    print("🎯 SUMMARY:")
    print("If you're still experiencing issues:")
    print("1. Check the Docker container logs: docker logs <container_name>")
    print("2. Verify database connectivity from within the container")
    print("3. Ensure all environment variables are properly passed to the container")
    print("4. Check that the application user has proper file permissions")
    print("=" * 70)

if __name__ == '__main__':
    main()
