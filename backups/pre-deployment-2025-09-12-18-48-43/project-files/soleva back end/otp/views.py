from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import logging

from .services import OTPService, OTPWorkflow
from .serializers import (
    OTPRequestSerializer, OTPVerificationSerializer, OTPResendSerializer,
    OTPStatusSerializer, UserRegistrationSerializer, PasswordResetSerializer
)
from .models import OTPRequest

logger = logging.getLogger(__name__)


class OTPRateThrottle(AnonRateThrottle):
    """Custom rate throttle for OTP requests"""
    scope = 'otp'
    rate = '10/min'  # 10 requests per minute


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Extract user agent from request"""
    return request.META.get('HTTP_USER_AGENT', '')


@method_decorator(csrf_exempt, name='dispatch')
class GenerateOTPView(APIView):
    """Generate OTP for registration or password reset"""
    permission_classes = [AllowAny]
    throttle_classes = [OTPRateThrottle]

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        otp_type = serializer.validated_data['otp_type']
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)

        try:
            if otp_type == 'registration':
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    return Response({
                        'success': False,
                        'message': 'A user with this email already exists'
                    }, status=status.HTTP_400_BAD_REQUEST)

                result = OTPWorkflow.initiate_registration_otp(
                    email=email,
                    ip_address=ip_address,
                    user_agent=user_agent
                )

            elif otp_type == 'password_reset':
                # Check if user exists
                if not User.objects.filter(email=email).exists():
                    # Don't reveal whether the email exists or not for security
                    return Response({
                        'success': True,
                        'message': 'If this email is registered, you will receive a verification code shortly.'
                    }, status=status.HTTP_200_OK)

                result = OTPWorkflow.initiate_password_reset_otp(
                    email=email,
                    ip_address=ip_address,
                    user_agent=user_agent
                )

            else:
                # Generic OTP generation
                success, message, otp_request = OTPService.generate_otp(
                    email=email,
                    otp_type=otp_type,
                    ip_address=ip_address,
                    user_agent=user_agent
                )

                result = {
                    'success': success,
                    'message': message,
                    'otp_status': OTPService.get_otp_status(email, otp_type) if success else None
                }

            if result['success']:
                logger.info(f"OTP generated successfully for {email} - {otp_type}")
                return Response({
                    'success': True,
                    'message': 'Verification code sent successfully',
                    'otp_status': result.get('otp_status')
                }, status=status.HTTP_200_OK)
            else:
                logger.warning(f"OTP generation failed for {email} - {otp_type}: {result['message']}")
                return Response({
                    'success': False,
                    'message': result['message']
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error generating OTP for {email}: {str(e)}")
            return Response({
                'success': False,
                'message': 'An error occurred while generating the verification code'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class VerifyOTPView(APIView):
    """Verify OTP code"""
    permission_classes = [AllowAny]
    throttle_classes = [OTPRateThrottle]

    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        otp_type = serializer.validated_data['otp_type']
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)

        try:
            success, message, otp_request = OTPService.verify_otp(
                email=email,
                provided_code=code,
                otp_type=otp_type,
                ip_address=ip_address,
                user_agent=user_agent
            )

            if success:
                logger.info(f"OTP verified successfully for {email} - {otp_type}")
                return Response({
                    'success': True,
                    'message': 'Verification code verified successfully',
                    'otp_request_id': otp_request.id if otp_request else None
                }, status=status.HTTP_200_OK)
            else:
                logger.warning(f"OTP verification failed for {email} - {otp_type}: {message}")
                
                # Get current status for remaining attempts info
                otp_status = OTPService.get_otp_status(email, otp_type)
                
                return Response({
                    'success': False,
                    'message': message,
                    'otp_status': otp_status
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error verifying OTP for {email}: {str(e)}")
            return Response({
                'success': False,
                'message': 'An error occurred while verifying the code'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class ResendOTPView(APIView):
    """Resend OTP code"""
    permission_classes = [AllowAny]
    throttle_classes = [OTPRateThrottle]

    def post(self, request):
        serializer = OTPResendSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        otp_type = serializer.validated_data['otp_type']
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)

        try:
            # For registration, check if user doesn't exist
            if otp_type == 'registration' and User.objects.filter(email=email).exists():
                return Response({
                    'success': False,
                    'message': 'A user with this email already exists'
                }, status=status.HTTP_400_BAD_REQUEST)

            # For password reset, check if user exists
            if otp_type == 'password_reset' and not User.objects.filter(email=email).exists():
                # Don't reveal whether the email exists or not for security
                return Response({
                    'success': True,
                    'message': 'If this email is registered, you will receive a verification code shortly.'
                }, status=status.HTTP_200_OK)

            user = User.objects.filter(email=email).first() if otp_type != 'registration' else None
            
            success, message, otp_request = OTPService.resend_otp(
                email=email,
                otp_type=otp_type,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )

            if success and otp_request:
                # Send the email
                from .services import EmailService
                email_sent = EmailService.send_otp_email(otp_request)
                
                if email_sent:
                    logger.info(f"OTP resent successfully for {email} - {otp_type}")
                    return Response({
                        'success': True,
                        'message': 'Verification code resent successfully',
                        'otp_status': OTPService.get_otp_status(email, otp_type)
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'success': False,
                        'message': 'Failed to send verification code'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                logger.warning(f"OTP resend failed for {email} - {otp_type}: {message}")
                return Response({
                    'success': False,
                    'message': message,
                    'otp_status': OTPService.get_otp_status(email, otp_type)
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error resending OTP for {email}: {str(e)}")
            return Response({
                'success': False,
                'message': 'An error occurred while resending the verification code'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class OTPStatusView(APIView):
    """Get OTP status for an email and type"""
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.query_params.get('email')
        otp_type = request.query_params.get('otp_type')

        if not email or not otp_type:
            return Response({
                'success': False,
                'message': 'Email and otp_type parameters are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_status = OTPService.get_otp_status(email, otp_type)
            serializer = OTPStatusSerializer(otp_status)
            
            return Response({
                'success': True,
                'otp_status': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error getting OTP status for {email}: {str(e)}")
            return Response({
                'success': False,
                'message': 'An error occurred while getting OTP status'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class CompleteRegistrationView(APIView):
    """Complete user registration with OTP verification"""
    permission_classes = [AllowAny]
    throttle_classes = [OTPRateThrottle]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']
        password = serializer.validated_data['password']
        first_name = serializer.validated_data.get('first_name', '')
        last_name = serializer.validated_data.get('last_name', '')

        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)

        try:
            # Verify OTP first
            success, message, otp_request = OTPService.verify_otp(
                email=email,
                provided_code=otp_code,
                otp_type='registration',
                ip_address=ip_address,
                user_agent=user_agent
            )

            if not success:
                return Response({
                    'success': False,
                    'message': message,
                    'otp_status': OTPService.get_otp_status(email, 'registration')
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create user account
            user = User.objects.create(
                username=email,  # Use email as username
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=make_password(password),
                is_active=True
            )

            logger.info(f"User registration completed successfully for {email}")
            
            return Response({
                'success': True,
                'message': 'Registration completed successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error completing registration for {email}: {str(e)}")
            return Response({
                'success': False,
                'message': 'An error occurred while completing registration'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class CompletePasswordResetView(APIView):
    """Complete password reset with OTP verification"""
    permission_classes = [AllowAny]
    throttle_classes = [OTPRateThrottle]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']
        new_password = serializer.validated_data['new_password']

        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)

        try:
            # Verify OTP first
            success, message, otp_request = OTPService.verify_otp(
                email=email,
                provided_code=otp_code,
                otp_type='password_reset',
                ip_address=ip_address,
                user_agent=user_agent
            )

            if not success:
                return Response({
                    'success': False,
                    'message': message,
                    'otp_status': OTPService.get_otp_status(email, 'password_reset')
                }, status=status.HTTP_400_BAD_REQUEST)

            # Update user password
            user = User.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()

            # Send security notification
            from .services import EmailService
            EmailService.send_security_notification(
                email=email,
                notification_type='password_reset_confirmation',
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )

            logger.info(f"Password reset completed successfully for {email}")
            
            return Response({
                'success': True,
                'message': 'Password reset completed successfully'
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error completing password reset for {email}: {str(e)}")
            return Response({
                'success': False,
                'message': 'An error occurred while resetting password'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
