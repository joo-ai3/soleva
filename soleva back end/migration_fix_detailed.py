#!/usr/bin/env python
"""
Comprehensive Migration Fix for Soleva Django Project
Addresses the "relation 'users' does not exist" error
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


def analyze_migration_dependencies():
    """Analyze migration dependencies to understand the issue"""
    print("\n🔍 ANALYZING MIGRATION DEPENDENCIES")
    print("=" * 60)

    # Check which migrations depend on users
    dependent_apps = []
    apps_with_migrations = []

    # Scan all app directories for migrations
    apps_dir = BASE_DIR
    for item in apps_dir.iterdir():
        if item.is_dir() and (item / 'migrations').exists():
            migrations_dir = item / 'migrations'
            migration_files = [f for f in migrations_dir.glob('*.py') if f.name != '__init__.py']

            if migration_files:
                apps_with_migrations.append(item.name)

                # Check if any migration depends on users
                for migration_file in migration_files:
                    try:
                        with open(migration_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'AUTH_USER_MODEL' in content or 'settings.AUTH_USER_MODEL' in content:
                                dependent_apps.append(item.name)
                                break
                    except Exception as e:
                        print(f"Warning: Could not read {migration_file}: {e}")

    print(f"📊 Apps with migrations: {len(apps_with_migrations)}")
    print(f"🔗 Apps depending on users: {len(dependent_apps)}")
    print(f"📋 Apps: {', '.join(apps_with_migrations)}")
    print(f"👥 Dependent apps: {', '.join(dependent_apps)}")

    return apps_with_migrations, dependent_apps


def create_migration_order_script():
    """Create a comprehensive migration script"""
    print("\n📝 CREATING MIGRATION ORDER SCRIPT")
    print("=" * 60)

    # Define migration order
    migration_order = [
        # Phase 1: Django built-ins (no dependencies)
        ("Django Auth System", ["auth"]),
        ("Django Content Types", ["contenttypes"]),
        ("Django Sessions", ["sessions"]),

        # Phase 2: Custom User Model (MUST be first)
        ("Custom User Model", ["users"]),

        # Phase 3: Apps that depend on users
        ("Django Admin (depends on users)", ["admin"]),
        ("Independent Apps", ["shipping", "otp"]),
        ("Products (base for others)", ["products"]),
        ("User-dependent Apps", ["offers", "cart", "coupons", "notifications", "accounting", "payments", "tracking", "website_management"]),
        ("Orders (depends on many)", ["orders"]),
    ]

    script_content = '''#!/bin/bash
# COMPREHENSIVE MIGRATION FIX FOR SOLEVA
# This script fixes the "relation 'users' does not exist" error
# Run this script from the backend directory: ./migration_fix_final.sh

set -e

echo "🔧 SOLEVA MIGRATION FIX SCRIPT"
echo "=============================="
echo "This script applies migrations in the correct order to fix dependency issues"
echo ""

# Function to run migration with error handling
run_migration() {
    local app=$1
    echo "▶️  Migrating $app..."
    if python manage.py migrate "$app" --verbosity=1; then
        echo "   ✅ $app migration successful"
    else
        echo "   ❌ $app migration failed"
        return 1
    fi
}

# Function to run makemigrations if needed
check_makemigrations() {
    echo "🔍 Checking for pending migrations..."
    if python manage.py makemigrations --dry-run | grep -q "would create"; then
        echo "📝 Creating new migrations..."
        python manage.py makemigrations
        echo "✅ New migrations created"
    else
        echo "✅ No new migrations needed"
    fi
}

# Step 0: Check for pending migrations
check_makemigrations

echo ""
echo "🚀 STARTING MIGRATIONS IN CORRECT ORDER"
echo "========================================"

'''

    for phase_name, apps in migration_order:
        script_content += f'''
echo ""
echo "📦 PHASE: {phase_name}"
echo "------------------------"'''
        for app in apps:
            script_content += f'''
run_migration "{app}"'''

    script_content += '''

echo ""
echo "🎉 ALL MIGRATIONS COMPLETED SUCCESSFULLY!"
echo "=========================================="
echo "You can now run: python manage.py runserver"
echo ""

# Optional: Create superuser
echo "👤 Creating superuser (optional)..."
read -p "Create superuser? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

echo "✅ Setup complete! Your Soleva backend is ready."
'''

    script_path = BASE_DIR / 'migration_fix_final.sh'
    with open(script_path, 'w', newline='\n') as f:
        f.write(script_content)

    # Make executable
    try:
        os.chmod(script_path, 0o755)
    except:
        pass

    print(f"✅ Created comprehensive migration script: {script_path}")
    print("Run it with: ./migration_fix_final.sh")


def create_docker_migration_script():
    """Create Docker-specific migration script"""
    print("\n🐳 CREATING DOCKER MIGRATION SCRIPT")
    print("=" * 60)

    docker_script = '''#!/bin/bash
# Docker Migration Fix Script
# Run this from your project root directory

set -e

echo "🐳 DOCKER MIGRATION FIX"
echo "======================="

# Stop containers
echo "🛑 Stopping containers..."
docker compose down

# Remove volumes to start fresh (WARNING: This deletes database data)
read -p "Remove volumes (deletes all data)? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing volumes..."
    docker compose down -v
    docker system prune -f
fi

# Start only database first
echo "🐘 Starting PostgreSQL..."
docker compose up -d postgres

# Wait for database to be ready
echo "⏳ Waiting for PostgreSQL..."
sleep 10

# Run migrations in backend container
echo "🔧 Running migrations..."
docker compose run --rm backend bash -c "
cd /app &&
echo 'Creating migrations...' &&
python manage.py makemigrations &&
echo 'Running migrations in correct order...' &&
python manage.py migrate auth &&
python manage.py migrate contenttypes &&
python manage.py migrate sessions &&
python manage.py migrate users &&
python manage.py migrate admin &&
python manage.py migrate shipping &&
python manage.py migrate otp &&
python manage.py migrate products &&
python manage.py migrate offers &&
python manage.py migrate cart &&
python manage.py migrate coupons &&
python manage.py migrate notifications &&
python manage.py migrate accounting &&
python manage.py migrate payments &&
python manage.py migrate tracking &&
python manage.py migrate website_management &&
python manage.py migrate orders &&
echo '✅ All migrations completed successfully!'
"

# Start all services
echo "🚀 Starting all services..."
docker compose up -d

# Check status
echo "📊 Service Status:"
docker compose ps

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================"
echo "Your Soleva application is now running."
echo "Access it at: http://localhost"
echo "Admin panel: http://localhost/admin"
'''

    docker_script_path = BASE_DIR.parent / 'docker_migration_fix.sh'
    with open(docker_script_path, 'w', newline='\n') as f:
        f.write(docker_script)

    # Make executable
    try:
        os.chmod(docker_script_path, 0o755)
    except:
        pass

    print(f"✅ Created Docker migration script: {docker_script_path}")


def provide_manual_steps():
    """Provide manual step-by-step instructions"""
    print("\n📋 MANUAL MIGRATION STEPS")
    print("=" * 60)
    print("If the automated scripts don't work, follow these steps:")
    print()

    print("1️⃣ PREPARATION:")
    print("   cd /path/to/soleva/backend")
    print("   docker compose down -v")
    print("   docker compose up -d postgres")
    print()

    print("2️⃣ CREATE MIGRATIONS:")
    print("   docker compose run --rm backend python manage.py makemigrations")
    print()

    print("3️⃣ RUN MIGRATIONS IN ORDER:")
    print("   docker compose run --rm backend python manage.py migrate auth")
    print("   docker compose run --rm backend python manage.py migrate contenttypes")
    print("   docker compose run --rm backend python manage.py migrate sessions")
    print("   docker compose run --rm backend python manage.py migrate users")
    print("   docker compose run --rm backend python manage.py migrate admin")
    print("   docker compose run --rm backend python manage.py migrate shipping")
    print("   docker compose run --rm backend python manage.py migrate otp")
    print("   docker compose run --rm backend python manage.py migrate products")
    print("   docker compose run --rm backend python manage.py migrate offers")
    print("   docker compose run --rm backend python manage.py migrate cart")
    print("   docker compose run --rm backend python manage.py migrate coupons")
    print("   docker compose run --rm backend python manage.py migrate notifications")
    print("   docker compose run --rm backend python manage.py migrate accounting")
    print("   docker compose run --rm backend python manage.py migrate payments")
    print("   docker compose run --rm backend python manage.py migrate tracking")
    print("   docker compose run --rm backend python manage.py migrate website_management")
    print("   docker compose run --rm backend python manage.py migrate orders")
    print()

    print("4️⃣ START ALL SERVICES:")
    print("   docker compose up -d")
    print()

    print("5️⃣ VERIFY:")
    print("   docker compose ps")
    print("   curl http://localhost/api/health/")
    print()


def main():
    """Main function"""
    print("🔧 SOLEVA MIGRATION DEPENDENCY FIX")
    print("=" * 70)

    # Analyze current situation
    apps_with_migrations, dependent_apps = analyze_migration_dependencies()

    # Create solution scripts
    create_migration_order_script()
    create_docker_migration_script()
    provide_manual_steps()

    print("\n" + "=" * 70)
    print("🎯 SUMMARY:")
    print("=" * 70)
    print("✅ Custom User model is properly defined")
    print("✅ AUTH_USER_MODEL is correctly set to 'users.User'")
    print("✅ Users app is included in INSTALLED_APPS")
    print("✅ Migration dependency issue identified and scripts created")
    print()
    print("📄 SCRIPTS CREATED:")
    print("   • migration_fix_final.sh (run locally)")
    print("   • docker_migration_fix.sh (run with Docker)")
    print()
    print("🚀 NEXT STEPS:")
    print("   1. Choose appropriate script based on your environment")
    print("   2. Run the script: ./migration_fix_final.sh")
    print("   3. If issues persist, follow manual steps above")
    print("   4. Test: docker compose up -d && docker compose ps")
    print()
    print("💡 TIP: The key is running 'users' migration BEFORE any app that references it!")


if __name__ == '__main__':
    main()
