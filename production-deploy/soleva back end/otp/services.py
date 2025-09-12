import logging
from typing import Tuple, Optional, Dict, Any
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from .models import OTPRequest, OTPConfiguration, SecurityNotification, OTPAttemptLog

logger = logging.getLogger(__name__)


class OTPService:
    """Comprehensive OTP service for generation, validation, and management"""

    @staticmethod
    def generate_otp(email: str, otp_type: str, user: Optional[User] = None, 
                    ip_address: str = None, user_agent: str = None) -> Tuple[bool, str, Optional[OTPRequest]]:
        """
        Generate a new OTP for the given email and type
        
        Returns:
            Tuple[bool, str, Optional[OTPRequest]]: (success, message, otp_request)
        """
        try:
            # Check rate limiting
            can_send, rate_message = OTPRequest.can_send_new_otp(email, otp_type)
            if not can_send:
                logger.warning(f"Rate limit exceeded for OTP request: {email} - {otp_type}")
                return False, rate_message, None

            # Invalidate previous OTPs
            OTPRequest.invalidate_previous_otps(email, otp_type)

            # Create new OTP request
            otp_request = OTPRequest.objects.create(
                email=email,
                user=user,
                otp_type=otp_type,
                ip_address=ip_address,
                user_agent=user_agent
            )

            logger.info(f"OTP generated successfully for {email} - {otp_type}")
            return True, "OTP generated successfully", otp_request

        except Exception as e:
            logger.error(f"Error generating OTP for {email}: {str(e)}")
            return False, "Failed to generate OTP", None

    @staticmethod
    def verify_otp(email: str, provided_code: str, otp_type: str, 
                  ip_address: str = None, user_agent: str = None) -> Tuple[bool, str, Optional[OTPRequest]]:
        """
        Verify the provided OTP code
        
        Returns:
            Tuple[bool, str, Optional[OTPRequest]]: (success, message, otp_request)
        """
        try:
            # Find the most recent valid OTP
            otp_request = OTPRequest.objects.filter(
                email=email,
                otp_type=otp_type,
                is_used=False,
                is_invalidated=False
            ).order_by('-created_at').first()

            if not otp_request:
                logger.warning(f"No valid OTP found for verification: {email} - {otp_type}")
                return False, "No valid OTP found", None

            # Log the attempt
            OTPAttemptLog.objects.create(
                otp_request=otp_request,
                provided_code=provided_code,
                is_successful=False,  # Will update if successful
                ip_address=ip_address,
                user_agent=user_agent
            )

            # Verify the code
            is_valid = otp_request.verify_code(provided_code)

            if is_valid:
                # Update the log entry to mark as successful
                OTPAttemptLog.objects.filter(
                    otp_request=otp_request,
                    provided_code=provided_code
                ).update(is_successful=True)
                
                logger.info(f"OTP verified successfully for {email} - {otp_type}")
                return True, "OTP verified successfully", otp_request
            else:
                remaining_attempts = otp_request.config.max_attempts - otp_request.attempts_count
                if remaining_attempts > 0:
                    message = f"Invalid OTP. {remaining_attempts} attempts remaining."
                else:
                    message = "Invalid OTP. Maximum attempts exceeded. Please request a new code."
                
                logger.warning(f"OTP verification failed for {email} - {otp_type}. Attempts: {otp_request.attempts_count}")
                return False, message, otp_request

        except Exception as e:
            logger.error(f"Error verifying OTP for {email}: {str(e)}")
            return False, "Failed to verify OTP", None

    @staticmethod
    def resend_otp(email: str, otp_type: str, user: Optional[User] = None,
                  ip_address: str = None, user_agent: str = None) -> Tuple[bool, str, Optional[OTPRequest]]:
        """
        Resend OTP with cooldown validation
        
        Returns:
            Tuple[bool, str, Optional[OTPRequest]]: (success, message, otp_request)
        """
        try:
            # Find the most recent OTP
            latest_otp = OTPRequest.objects.filter(
                email=email,
                otp_type=otp_type
            ).order_by('-created_at').first()

            if latest_otp and not latest_otp.can_resend():
                countdown = latest_otp.get_resend_countdown()
                minutes = countdown // 60
                seconds = countdown % 60
                return False, f"Please wait {minutes:02d}:{seconds:02d} before requesting a new code", None

            # Generate new OTP
            return OTPService.generate_otp(email, otp_type, user, ip_address, user_agent)

        except Exception as e:
            logger.error(f"Error resending OTP for {email}: {str(e)}")
            return False, "Failed to resend OTP", None

    @staticmethod
    def get_otp_status(email: str, otp_type: str) -> Dict[str, Any]:
        """
        Get current OTP status for an email and type
        
        Returns:
            Dict containing OTP status information
        """
        try:
            latest_otp = OTPRequest.objects.filter(
                email=email,
                otp_type=otp_type
            ).order_by('-created_at').first()

            if not latest_otp:
                return {
                    'has_otp': False,
                    'can_resend': True,
                    'resend_countdown': 0,
                    'attempts_remaining': 0
                }

            config = latest_otp.config
            return {
                'has_otp': True,
                'is_valid': latest_otp.is_valid(),
                'can_resend': latest_otp.can_resend(),
                'resend_countdown': latest_otp.get_resend_countdown(),
                'attempts_remaining': max(0, config.max_attempts - latest_otp.attempts_count),
                'expires_at': latest_otp.expires_at.isoformat(),
                'created_at': latest_otp.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting OTP status for {email}: {str(e)}")
            return {
                'has_otp': False,
                'can_resend': True,
                'resend_countdown': 0,
                'attempts_remaining': 0
            }


class EmailService:
    """Professional email service for OTP and security notifications"""

    @staticmethod
    def send_otp_email(otp_request: OTPRequest) -> bool:
        """Send OTP email with professional template"""
        try:
            context = {
                'code': otp_request.code,
                'email': otp_request.email,
                'otp_type': otp_request.get_otp_type_display(),
                'expires_minutes': otp_request.config.expiry_minutes,
                'company_name': getattr(settings, 'COMPANY_NAME', 'Soleva'),
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@soleva.com'),
                'website_url': getattr(settings, 'WEBSITE_URL', 'https://soleva.com'),
            }

            # Load appropriate template based on OTP type
            template_name = f'emails/otp_{otp_request.otp_type}.html'
            try:
                html_message = render_to_string(template_name, context)
            except:
                # Fallback to generic template
                html_message = render_to_string('emails/otp_generic.html', context)

            plain_message = strip_tags(html_message)
            
            subject_map = {
                'registration': f'Welcome to {context["company_name"]} - Verify Your Email',
                'password_reset': f'Password Reset Code - {context["company_name"]}',
                'login_verification': f'Login Verification Code - {context["company_name"]}',
                'email_verification': f'Email Verification Code - {context["company_name"]}',
            }
            
            subject = subject_map.get(otp_request.otp_type, f'Verification Code - {context["company_name"]}')

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@soleva.com'),
                recipient_list=[otp_request.email],
                html_message=html_message,
                fail_silently=False
            )

            logger.info(f"OTP email sent successfully to {otp_request.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send OTP email to {otp_request.email}: {str(e)}")
            return False

    @staticmethod
    def send_security_notification(email: str, notification_type: str, 
                                 user: Optional[User] = None, **context_data) -> bool:
        """Send security notification email"""
        try:
            base_context = {
                'email': email,
                'user_name': user.get_full_name() if user else email.split('@')[0],
                'company_name': getattr(settings, 'COMPANY_NAME', 'Soleva'),
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@soleva.com'),
                'website_url': getattr(settings, 'WEBSITE_URL', 'https://soleva.com'),
                'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            }
            base_context.update(context_data)

            template_name = f'emails/security_{notification_type}.html'
            try:
                html_message = render_to_string(template_name, base_context)
            except:
                # Fallback to generic security template
                html_message = render_to_string('emails/security_generic.html', base_context)

            plain_message = strip_tags(html_message)

            subject_map = {
                'password_reset_alert': f'Security Alert: Password Reset Request - {base_context["company_name"]}',
                'suspicious_activity': f'Security Alert: Suspicious Activity - {base_context["company_name"]}',
                'account_locked': f'Security Alert: Account Locked - {base_context["company_name"]}',
                'login_from_new_device': f'Security Alert: New Device Login - {base_context["company_name"]}',
            }

            subject = subject_map.get(notification_type, f'Security Alert - {base_context["company_name"]}')

            # Create notification record
            notification = SecurityNotification.objects.create(
                user=user,
                email=email,
                notification_type=notification_type,
                subject=subject,
                message=plain_message
            )

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@soleva.com'),
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False
            )

            notification.is_sent = True
            notification.sent_at = timezone.now()
            notification.save()

            logger.info(f"Security notification sent successfully to {email}: {notification_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to send security notification to {email}: {str(e)}")
            return False


class OTPWorkflow:
    """High-level OTP workflow management"""

    @staticmethod
    def initiate_registration_otp(email: str, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Initiate OTP for user registration"""
        success, message, otp_request = OTPService.generate_otp(
            email=email,
            otp_type='registration',
            ip_address=ip_address,
            user_agent=user_agent
        )

        if success and otp_request:
            email_sent = EmailService.send_otp_email(otp_request)
            return {
                'success': success and email_sent,
                'message': message if email_sent else 'OTP generated but email failed to send',
                'otp_status': OTPService.get_otp_status(email, 'registration')
            }

        return {
            'success': success,
            'message': message,
            'otp_status': None
        }

    @staticmethod
    def initiate_password_reset_otp(email: str, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Initiate OTP for password reset with security notification"""
        try:
            user = User.objects.filter(email=email).first()
        except:
            user = None

        # Generate OTP
        success, message, otp_request = OTPService.generate_otp(
            email=email,
            otp_type='password_reset',
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )

        if success and otp_request:
            # Send OTP email
            otp_email_sent = EmailService.send_otp_email(otp_request)
            
            # Send security notification
            security_email_sent = EmailService.send_security_notification(
                email=email,
                notification_type='password_reset_alert',
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )

            return {
                'success': success and otp_email_sent,
                'message': message if otp_email_sent else 'OTP generated but email failed to send',
                'security_notification_sent': security_email_sent,
                'otp_status': OTPService.get_otp_status(email, 'password_reset')
            }

        return {
            'success': success,
            'message': message,
            'security_notification_sent': False,
            'otp_status': None
        }
