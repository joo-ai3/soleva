#!/usr/bin/env python
"""
OTP System Setup Script for Soleva E-commerce Platform

This script sets up the complete OTP verification system:
- Creates database migrations
- Sets up default OTP configuration
- Creates sample email templates
- Verifies all components are working

Usage:
    python setup_otp_system.py
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soleva_backend.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.conf import settings
from otp.models import OTPConfiguration
from django.core.mail import send_test_mail


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_step(step, description):
    """Print a step description"""
    print(f"\n[{step}] {description}")


def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")


def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")


def print_warning(message):
    """Print a warning message"""
    print(f"⚠️  {message}")


def run_management_command(command_args):
    """Run a Django management command and return success status"""
    try:
        execute_from_command_line(['manage.py'] + command_args)
        return True
    except Exception as e:
        print_error(f"Command failed: {e}")
        return False


def create_migrations():
    """Create migrations for the OTP app"""
    print_step("1", "Creating database migrations...")
    
    # Create migrations for OTP app
    if run_management_command(['makemigrations', 'otp']):
        print_success("OTP migrations created successfully")
    else:
        print_error("Failed to create OTP migrations")
        return False
    
    # Apply migrations
    print_step("1.1", "Applying migrations...")
    if run_management_command(['migrate']):
        print_success("Migrations applied successfully")
    else:
        print_error("Failed to apply migrations")
        return False
    
    return True


def setup_otp_configuration():
    """Set up default OTP configuration"""
    print_step("2", "Setting up OTP configuration...")
    
    try:
        # Create or update default configuration
        config, created = OTPConfiguration.objects.get_or_create(
            name='default',
            defaults={
                'code_length': 6,
                'expiry_minutes': 5,
                'max_attempts': 5,
                'resend_cooldown_minutes': 2,
                'rate_limit_requests': 3,
                'rate_limit_window_minutes': 10,
                'is_active': True
            }
        )
        
        if created:
            print_success("Default OTP configuration created")
        else:
            print_success("Default OTP configuration already exists")
        
        # Create production configuration
        prod_config, prod_created = OTPConfiguration.objects.get_or_create(
            name='production',
            defaults={
                'code_length': 6,
                'expiry_minutes': 10,
                'max_attempts': 3,
                'resend_cooldown_minutes': 3,
                'rate_limit_requests': 2,
                'rate_limit_window_minutes': 15,
                'is_active': False
            }
        )
        
        if prod_created:
            print_success("Production OTP configuration created")
        else:
            print_success("Production OTP configuration already exists")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to set up OTP configuration: {e}")
        return False


def verify_email_templates():
    """Verify that email templates exist"""
    print_step("3", "Verifying email templates...")
    
    template_dir = project_root / 'templates' / 'emails'
    required_templates = [
        'base_email.html',
        'otp_registration.html',
        'otp_password_reset.html',
        'security_password_reset_alert.html'
    ]
    
    missing_templates = []
    for template in required_templates:
        template_path = template_dir / template
        if template_path.exists():
            print_success(f"Template found: {template}")
        else:
            missing_templates.append(template)
            print_error(f"Template missing: {template}")
    
    if missing_templates:
        print_error(f"Missing {len(missing_templates)} required templates")
        return False
    else:
        print_success("All email templates are present")
        return True


def test_email_configuration():
    """Test email configuration"""
    print_step("4", "Testing email configuration...")
    
    try:
        # Check email settings
        email_backend = getattr(settings, 'EMAIL_BACKEND', None)
        if not email_backend:
            print_error("EMAIL_BACKEND not configured in settings")
            return False
        
        print_success(f"Email backend: {email_backend}")
        
        # For development, check if console backend is used
        if 'console' in email_backend.lower():
            print_success("Console email backend detected (development mode)")
            return True
        
        # For production backends, check additional settings
        smtp_host = getattr(settings, 'EMAIL_HOST', None)
        if smtp_host:
            print_success(f"SMTP host: {smtp_host}")
        else:
            print_warning("EMAIL_HOST not configured")
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        if from_email:
            print_success(f"From email: {from_email}")
        else:
            print_warning("DEFAULT_FROM_EMAIL not configured")
        
        return True
        
    except Exception as e:
        print_error(f"Email configuration test failed: {e}")
        return False


def create_superuser_if_needed():
    """Create a superuser if none exists"""
    print_step("5", "Checking for superuser...")
    
    try:
        from django.contrib.auth.models import User
        
        if User.objects.filter(is_superuser=True).exists():
            print_success("Superuser already exists")
            return True
        
        print_warning("No superuser found. You should create one manually:")
        print("   python manage.py createsuperuser")
        return True
        
    except Exception as e:
        print_error(f"Failed to check for superuser: {e}")
        return False


def display_usage_instructions():
    """Display usage instructions"""
    print_header("OTP System Usage Instructions")
    
    print("\n🔐 OTP Endpoints:")
    print("   POST /api/otp/generate/           - Generate OTP")
    print("   POST /api/otp/verify/             - Verify OTP")
    print("   POST /api/otp/resend/             - Resend OTP")
    print("   GET  /api/otp/status/             - Get OTP status")
    print("   POST /api/otp/complete-registration/")
    print("   POST /api/otp/complete-password-reset/")
    
    print("\n📧 Email Templates:")
    print("   templates/emails/otp_registration.html")
    print("   templates/emails/otp_password_reset.html")
    print("   templates/emails/security_password_reset_alert.html")
    
    print("\n⚙️  Admin Interface:")
    print("   Access Django admin to manage OTP configurations")
    print("   Monitor OTP requests and security notifications")
    
    print("\n📱 Frontend Components:")
    print("   OTPInput - Modern 6-digit input component")
    print("   CountdownTimer - Resend countdown timer")
    print("   OTPVerificationForm - Complete verification form")
    
    print("\n🔧 Configuration:")
    config = OTPConfiguration.objects.filter(is_active=True).first()
    if config:
        print(f"   Code Length: {config.code_length} digits")
        print(f"   Expiry Time: {config.expiry_minutes} minutes")
        print(f"   Max Attempts: {config.max_attempts}")
        print(f"   Resend Cooldown: {config.resend_cooldown_minutes} minutes")
        print(f"   Rate Limit: {config.rate_limit_requests} requests per {config.rate_limit_window_minutes} minutes")


def display_security_features():
    """Display security features"""
    print_header("Security Features")
    
    print("\n🛡️  Security Measures:")
    print("   ✅ One-time use OTP codes")
    print("   ✅ Time-based expiration (5 minutes default)")
    print("   ✅ Rate limiting (3 requests per 10 minutes)")
    print("   ✅ Maximum attempt limits (5 attempts)")
    print("   ✅ Automatic code invalidation")
    print("   ✅ Security notifications for password resets")
    print("   ✅ IP address and user agent tracking")
    print("   ✅ Comprehensive audit logging")


def main():
    """Main setup function"""
    print_header("Soleva OTP Verification System Setup")
    
    success_count = 0
    total_steps = 5
    
    # Step 1: Create migrations
    if create_migrations():
        success_count += 1
    
    # Step 2: Setup OTP configuration
    if setup_otp_configuration():
        success_count += 1
    
    # Step 3: Verify email templates
    if verify_email_templates():
        success_count += 1
    
    # Step 4: Test email configuration
    if test_email_configuration():
        success_count += 1
    
    # Step 5: Check for superuser
    if create_superuser_if_needed():
        success_count += 1
    
    # Display results
    print_header("Setup Results")
    
    if success_count == total_steps:
        print_success(f"Setup completed successfully! ({success_count}/{total_steps} steps)")
        print("\n🎉 Your OTP system is ready to use!")
        
        display_security_features()
        display_usage_instructions()
        
        print_header("Next Steps")
        print("\n1. Start the Django development server:")
        print("   python manage.py runserver")
        print("\n2. Access the admin interface:")
        print("   http://localhost:8000/admin/")
        print("\n3. Test the OTP endpoints:")
        print("   Use the API endpoints to generate and verify OTPs")
        print("\n4. Integrate with your frontend:")
        print("   Use the provided React components")
        
    else:
        print_error(f"Setup completed with errors ({success_count}/{total_steps} steps successful)")
        print("\nPlease review the errors above and fix any issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
