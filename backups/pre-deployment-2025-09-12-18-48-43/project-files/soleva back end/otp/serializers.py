from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
import re


class OTPRequestSerializer(serializers.Serializer):
    """Serializer for OTP generation requests"""
    email = serializers.EmailField(validators=[EmailValidator()])
    otp_type = serializers.ChoiceField(choices=[
        ('registration', 'Registration'),
        ('password_reset', 'Password Reset'),
        ('login_verification', 'Login Verification'),
        ('email_verification', 'Email Verification'),
    ])

    def validate_email(self, value):
        """Validate email format and basic checks"""
        # Basic email validation
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Email is required")
        
        # Additional email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise serializers.ValidationError("Please enter a valid email address")
        
        return value.lower().strip()


class OTPVerificationSerializer(serializers.Serializer):
    """Serializer for OTP verification requests"""
    email = serializers.EmailField(validators=[EmailValidator()])
    code = serializers.CharField(min_length=4, max_length=10)
    otp_type = serializers.ChoiceField(choices=[
        ('registration', 'Registration'),
        ('password_reset', 'Password Reset'),
        ('login_verification', 'Login Verification'),
        ('email_verification', 'Email Verification'),
    ])

    def validate_email(self, value):
        """Validate email format"""
        return value.lower().strip()

    def validate_code(self, value):
        """Validate OTP code format"""
        # Remove any spaces or special characters
        cleaned_code = re.sub(r'[^0-9]', '', value)
        
        if not cleaned_code:
            raise serializers.ValidationError("OTP code must contain only numbers")
        
        if len(cleaned_code) < 4 or len(cleaned_code) > 10:
            raise serializers.ValidationError("OTP code must be between 4 and 10 digits")
        
        return cleaned_code


class OTPResendSerializer(serializers.Serializer):
    """Serializer for OTP resend requests"""
    email = serializers.EmailField(validators=[EmailValidator()])
    otp_type = serializers.ChoiceField(choices=[
        ('registration', 'Registration'),
        ('password_reset', 'Password Reset'),
        ('login_verification', 'Login Verification'),
        ('email_verification', 'Email Verification'),
    ])

    def validate_email(self, value):
        """Validate email format"""
        return value.lower().strip()


class OTPStatusSerializer(serializers.Serializer):
    """Serializer for OTP status responses"""
    has_otp = serializers.BooleanField()
    is_valid = serializers.BooleanField(required=False)
    can_resend = serializers.BooleanField()
    resend_countdown = serializers.IntegerField()
    attempts_remaining = serializers.IntegerField()
    expires_at = serializers.CharField(required=False)
    created_at = serializers.CharField(required=False)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with OTP verification"""
    email = serializers.EmailField(validators=[EmailValidator()])
    password = serializers.CharField(min_length=8, write_only=True)
    password_confirm = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    otp_code = serializers.CharField(min_length=4, max_length=10, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name', 'otp_code']

    def validate_email(self, value):
        """Validate email and check if it's already registered"""
        email = value.lower().strip()
        
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with this email already exists")
        
        return email

    def validate_password(self, value):
        """Validate password strength"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        # Check for at least one number
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number")
        
        # Check for at least one letter
        if not re.search(r'[a-zA-Z]', value):
            raise serializers.ValidationError("Password must contain at least one letter")
        
        return value

    def validate(self, data):
        """Validate password confirmation"""
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match'
            })
        
        return data

    def validate_otp_code(self, value):
        """Validate OTP code format"""
        cleaned_code = re.sub(r'[^0-9]', '', value)
        
        if not cleaned_code:
            raise serializers.ValidationError("OTP code must contain only numbers")
        
        return cleaned_code


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset with OTP verification"""
    email = serializers.EmailField(validators=[EmailValidator()])
    otp_code = serializers.CharField(min_length=4, max_length=10)
    new_password = serializers.CharField(min_length=8, write_only=True)
    new_password_confirm = serializers.CharField(min_length=8, write_only=True)

    def validate_email(self, value):
        """Validate email and check if user exists"""
        email = value.lower().strip()
        
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("No user found with this email address")
        
        return email

    def validate_new_password(self, value):
        """Validate new password strength"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        # Check for at least one number
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number")
        
        # Check for at least one letter
        if not re.search(r'[a-zA-Z]', value):
            raise serializers.ValidationError("Password must contain at least one letter")
        
        return value

    def validate(self, data):
        """Validate password confirmation"""
        if data.get('new_password') != data.get('new_password_confirm'):
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match'
            })
        
        return data

    def validate_otp_code(self, value):
        """Validate OTP code format"""
        cleaned_code = re.sub(r'[^0-9]', '', value)
        
        if not cleaned_code:
            raise serializers.ValidationError("OTP code must contain only numbers")
        
        return cleaned_code
