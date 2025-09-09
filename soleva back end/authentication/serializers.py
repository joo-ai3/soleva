from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from phonenumber_field.serializerfields import PhoneNumberField
import random
import string

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['user_id'] = user.id
        token['email'] = user.email
        token['full_name'] = user.full_name
        token['language_preference'] = user.language_preference
        token['is_verified'] = user.is_verified
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user data to response
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'full_name': self.user.full_name,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'phone_number': str(self.user.phone_number) if self.user.phone_number else None,
            'language_preference': self.user.language_preference,
            'is_verified': self.user.is_verified,
            'email_notifications': self.user.email_notifications,
            'sms_notifications': self.user.sms_notifications,
            'push_notifications': self.user.push_notifications,
        }
        
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    phone_number = PhoneNumberField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number',
            'language_preference', 'gender', 'date_of_birth'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'username': {'required': True},
        }
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def validate_username(self, value):
        """Validate username uniqueness"""
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value.lower()
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Generate verification code
        verification_code = ''.join(random.choices(string.digits, k=6))
        
        user = User.objects.create_user(
            password=password,
            verification_code=verification_code,
            **validated_data
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """Login serializer"""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Try to authenticate with email
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                # Try to find user by email and authenticate
                try:
                    user_obj = User.objects.get(email__iexact=email)
                    user = authenticate(
                        request=self.context.get('request'),
                        username=user_obj.username,
                        password=password
                    )
                except User.DoesNotExist:
                    pass
            
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include "email" and "password".')


class PasswordResetRequestSerializer(serializers.Serializer):
    """Password reset request serializer"""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validate that user exists"""
        try:
            User.objects.get(email__iexact=value, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("No active user found with this email address.")
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Password reset confirmation serializer"""
    
    email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate password confirmation and verification code"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Password fields didn't match."})
        
        try:
            user = User.objects.get(email__iexact=attrs['email'], is_active=True)
            if user.verification_code != attrs['verification_code']:
                raise serializers.ValidationError({"verification_code": "Invalid verification code."})
            
            # Check if code is expired (valid for 30 minutes)
            from django.utils import timezone
            from datetime import timedelta
            
            if user.verification_code_expires and user.verification_code_expires < timezone.now():
                raise serializers.ValidationError({"verification_code": "Verification code has expired."})
            
            attrs['user'] = user
            
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found."})
        
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer"""
    
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_current_password(self, value):
        """Validate current password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Password fields didn't match."})
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """Email verification serializer"""
    
    email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=6)
    
    def validate(self, attrs):
        """Validate verification code"""
        try:
            user = User.objects.get(email__iexact=attrs['email'], is_active=True)
            if user.verification_code != attrs['verification_code']:
                raise serializers.ValidationError({"verification_code": "Invalid verification code."})
            
            if user.is_verified:
                raise serializers.ValidationError({"verification_code": "Email is already verified."})
            
            # Check if code is expired (valid for 24 hours)
            from django.utils import timezone
            from datetime import timedelta
            
            if user.verification_code_expires and user.verification_code_expires < timezone.now():
                raise serializers.ValidationError({"verification_code": "Verification code has expired."})
            
            attrs['user'] = user
            
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found."})
        
        return attrs


class ResendVerificationSerializer(serializers.Serializer):
    """Resend verification code serializer"""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validate that user exists and is not verified"""
        try:
            user = User.objects.get(email__iexact=value, is_active=True)
            if user.is_verified:
                raise serializers.ValidationError("Email is already verified.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        return value.lower()


class SocialAuthSerializer(serializers.Serializer):
    """Social authentication serializer"""
    
    provider = serializers.ChoiceField(choices=['google', 'facebook', 'apple'])
    access_token = serializers.CharField()
    
    def validate(self, attrs):
        """Validate social auth token"""
        provider = attrs.get('provider')
        access_token = attrs.get('access_token')
        
        # Here you would implement actual social auth validation
        # For now, this is a placeholder
        
        attrs['user_data'] = {
            'email': 'user@example.com',  # This would come from the social provider
            'first_name': 'John',
            'last_name': 'Doe',
        }
        
        return attrs
