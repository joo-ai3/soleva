from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
import string

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    SocialAuthSerializer
)

User = get_user_model()


class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'

class RegisterRateThrottle(AnonRateThrottle):
    scope = 'register'

class PasswordResetRateThrottle(AnonRateThrottle):
    scope = 'password-reset'


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view"""
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]


class RegisterView(APIView):
    """User registration view"""
    
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegisterRateThrottle]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Send verification email (implement this in your notification system)
            # send_verification_email.delay(user.id)
            
            return Response({
                'message': 'Registration successful. Please check your email for verification code.',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'is_verified': user.is_verified,
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User login view"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            # Update last login
            user.last_login = timezone.now()
            user.last_login_ip = self.get_client_ip(request)
            user.save(update_fields=['last_login', 'last_login_ip'])
            
            return Response({
                'access': str(access),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': str(user.phone_number) if user.phone_number else None,
                    'language_preference': user.language_preference,
                    'is_verified': user.is_verified,
                    'email_notifications': user.email_notifications,
                    'sms_notifications': user.sms_notifications,
                    'push_notifications': user.push_notifications,
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(APIView):
    """User logout view"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'message': 'Successfully logged out.'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': 'Invalid token.'
            }, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """Password reset request view"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email__iexact=email, is_active=True)
            
            # Generate verification code
            verification_code = ''.join(random.choices(string.digits, k=6))
            user.verification_code = verification_code
            user.verification_code_expires = timezone.now() + timedelta(minutes=30)
            user.save(update_fields=['verification_code', 'verification_code_expires'])
            
            # Send password reset email (implement this in your notification system)
            # send_password_reset_email.delay(user.id)
            
            return Response({
                'message': 'Password reset code sent to your email.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """Password reset confirmation view"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            new_password = serializer.validated_data['new_password']
            
            # Update password
            user.set_password(new_password)
            user.verification_code = None
            user.verification_code_expires = None
            user.save(update_fields=['password', 'verification_code', 'verification_code_expires'])
            
            return Response({
                'message': 'Password reset successful.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """Change password view"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']
            
            # Update password
            user.set_password(new_password)
            user.save(update_fields=['password'])
            
            return Response({
                'message': 'Password changed successfully.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    """Email verification view"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Mark email as verified
            user.is_verified = True
            user.verification_code = None
            user.verification_code_expires = None
            user.save(update_fields=['is_verified', 'verification_code', 'verification_code_expires'])
            
            return Response({
                'message': 'Email verified successfully.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationView(APIView):
    """Resend verification code view"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email__iexact=email, is_active=True)
            
            # Generate new verification code
            verification_code = ''.join(random.choices(string.digits, k=6))
            user.verification_code = verification_code
            user.verification_code_expires = timezone.now() + timedelta(hours=24)
            user.save(update_fields=['verification_code', 'verification_code_expires'])
            
            # Send verification email (implement this in your notification system)
            # send_verification_email.delay(user.id)
            
            return Response({
                'message': 'Verification code sent to your email.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SocialAuthView(APIView):
    """Social authentication view"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = SocialAuthSerializer(data=request.data)
        if serializer.is_valid():
            provider = serializer.validated_data['provider']
            user_data = serializer.validated_data['user_data']
            
            # Try to find existing user
            try:
                user = User.objects.get(email__iexact=user_data['email'])
            except User.DoesNotExist:
                # Create new user
                username = user_data['email'].split('@')[0]
                # Ensure unique username
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_verified=True,  # Social auth users are considered verified
                )
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            # Update last login
            user.last_login = timezone.now()
            user.last_login_ip = self.get_client_ip(request)
            user.save(update_fields=['last_login', 'last_login_ip'])
            
            return Response({
                'access': str(access),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': str(user.phone_number) if user.phone_number else None,
                    'language_preference': user.language_preference,
                    'is_verified': user.is_verified,
                    'email_notifications': user.email_notifications,
                    'sms_notifications': user.sms_notifications,
                    'push_notifications': user.push_notifications,
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    """Get user profile"""
    user = request.user
    return Response({
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'full_name': user.full_name,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': str(user.phone_number) if user.phone_number else None,
        'date_of_birth': user.date_of_birth,
        'gender': user.gender,
        'language_preference': user.language_preference,
        'is_verified': user.is_verified,
        'email_notifications': user.email_notifications,
        'sms_notifications': user.sms_notifications,
        'push_notifications': user.push_notifications,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'message': 'Soleva API is running'
    }, status=status.HTTP_200_OK)
