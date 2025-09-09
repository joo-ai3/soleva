#!/usr/bin/env python
"""
Soleva Backend Setup Script
This script helps set up the Soleva e-commerce backend
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soleva_backend.settings')

# Setup Django
django.setup()

from django.contrib.auth import get_user_model
from shipping.models import Governorate, City
from products.models import Category, Brand
from payments.models import PaymentMethod

User = get_user_model()


def create_superuser():
    """Create superuser if it doesn't exist"""
    print("Creating superuser...")
    
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@soleva.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print("✓ Superuser created (admin@soleva.com / admin123)")
    else:
        print("✓ Superuser already exists")


def load_egypt_locations():
    """Load Egypt governorates and cities"""
    print("Loading Egypt locations...")
    
    # Sample governorates
    governorates_data = [
        {'name_en': 'Cairo', 'name_ar': 'القاهرة', 'code': 'CAI', 'base_shipping_cost': 30.00},
        {'name_en': 'Giza', 'name_ar': 'الجيزة', 'code': 'GIZ', 'base_shipping_cost': 30.00},
        {'name_en': 'Alexandria', 'name_ar': 'الإسكندرية', 'code': 'ALX', 'base_shipping_cost': 40.00},
        {'name_en': 'Dakahlia', 'name_ar': 'الدقهلية', 'code': 'DK', 'base_shipping_cost': 50.00},
        {'name_en': 'Sharkia', 'name_ar': 'الشرقية', 'code': 'SHR', 'base_shipping_cost': 50.00},
    ]
    
    cities_data = {
        'CAI': ['Nasr City', 'Heliopolis', 'Maadi', 'Downtown', 'New Cairo'],
        'GIZ': ['Dokki', 'Mohandessin', 'Haram', '6th of October', 'Sheikh Zayed'],
        'ALX': ['Sporting', 'Stanley', 'Sidi Gaber', 'Smouha', 'Miami'],
    }
    
    for gov_data in governorates_data:
        gov, created = Governorate.objects.get_or_create(
            code=gov_data['code'],
            defaults=gov_data
        )
        if created:
            print(f"✓ Created governorate: {gov.name_en}")
        
        # Add cities
        if gov_data['code'] in cities_data:
            for city_name in cities_data[gov_data['code']]:
                city, created = City.objects.get_or_create(
                    governorate=gov,
                    name_en=city_name,
                    defaults={
                        'name_ar': city_name,  # Placeholder
                        'additional_shipping_cost': 0.00,
                        'estimated_delivery_days': 2
                    }
                )
                if created:
                    print(f"  ✓ Created city: {city.name_en}")


def create_sample_categories():
    """Create sample product categories"""
    print("Creating sample categories...")
    
    categories = [
        {'name_en': 'Fashion', 'name_ar': 'أزياء', 'slug': 'fashion'},
        {'name_en': 'Electronics', 'name_ar': 'إلكترونيات', 'slug': 'electronics'},
        {'name_en': 'Home & Garden', 'name_ar': 'المنزل والحديقة', 'slug': 'home-garden'},
        {'name_en': 'Beauty', 'name_ar': 'جمال', 'slug': 'beauty'},
        {'name_en': 'Sports', 'name_ar': 'رياضة', 'slug': 'sports'},
    ]
    
    for cat_data in categories:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        if created:
            print(f"✓ Created category: {category.name_en}")


def create_sample_brands():
    """Create sample brands"""
    print("Creating sample brands...")
    
    brands = [
        {'name': 'Soleva', 'slug': 'soleva'},
        {'name': 'Premium Brand', 'slug': 'premium-brand'},
        {'name': 'Quality Plus', 'slug': 'quality-plus'},
    ]
    
    for brand_data in brands:
        brand, created = Brand.objects.get_or_create(
            slug=brand_data['slug'],
            defaults=brand_data
        )
        if created:
            print(f"✓ Created brand: {brand.name}")


def create_payment_methods():
    """Create payment methods"""
    print("Creating payment methods...")
    
    methods = [
        {
            'name': 'Cash on Delivery',
            'code': 'cash_on_delivery',
            'display_name_en': 'Cash on Delivery',
            'display_name_ar': 'الدفع عند الاستلام',
            'requires_gateway': False,
            'min_amount': 50.00,
            'display_order': 1
        },
        {
            'name': 'Paymob',
            'code': 'paymob',
            'display_name_en': 'Credit/Debit Card',
            'display_name_ar': 'بطاقة ائتمان/خصم',
            'requires_gateway': True,
            'min_amount': 1.00,
            'display_order': 2
        },
        {
            'name': 'Stripe',
            'code': 'stripe',
            'display_name_en': 'International Cards',
            'display_name_ar': 'البطاقات الدولية',
            'requires_gateway': True,
            'min_amount': 1.00,
            'display_order': 3,
            'is_active': False  # Disabled by default
        }
    ]
    
    for method_data in methods:
        method, created = PaymentMethod.objects.get_or_create(
            code=method_data['code'],
            defaults=method_data
        )
        if created:
            print(f"✓ Created payment method: {method.name}")


def run_migrations():
    """Run database migrations"""
    print("Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    print("✓ Migrations completed")


def collect_static():
    """Collect static files"""
    print("Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    print("✓ Static files collected")


def main():
    """Main setup function"""
    print("🚀 Setting up Soleva E-commerce Backend...")
    print("=" * 50)
    
    try:
        # Run migrations first
        run_migrations()
        
        # Create initial data
        create_superuser()
        load_egypt_locations()
        create_sample_categories()
        create_sample_brands()
        create_payment_methods()
        
        # Collect static files
        collect_static()
        
        print("\n" + "=" * 50)
        print("✅ Setup completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Update your .env file with proper credentials")
        print("2. Configure Redis and PostgreSQL")
        print("3. Set up Celery workers")
        print("4. Configure payment gateways")
        print("5. Add tracking pixels configuration")
        print("\n🌐 Admin Panel: http://localhost:8000/admin/")
        print("📧 Admin Login: admin@soleva.com")
        print("🔑 Password: admin123")
        print("\n🚀 Start server: python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
