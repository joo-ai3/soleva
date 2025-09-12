from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
import secrets
import string
from datetime import timedelta


class OTPConfiguration(models.Model):
    """Configuration for OTP settings"""
    name = models.CharField(max_length=50, unique=True, default='default')
    code_length = models.IntegerField(default=6)
    expiry_minutes = models.IntegerField(default=5)
    max_attempts = models.IntegerField(default=5)
    resend_cooldown_minutes = models.IntegerField(default=2)
    rate_limit_requests = models.IntegerField(default=3)
    rate_limit_window_minutes = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OTP Config: {self.name}"

    class Meta:
        verbose_name = "OTP Configuration"
        verbose_name_plural = "OTP Configurations"


class OTPRequest(models.Model):
    """OTP request tracking for rate limiting"""
    OTP_TYPES = [
        ('registration', 'Registration'),
        ('password_reset', 'Password Reset'),
        ('login_verification', 'Login Verification'),
        ('email_verification', 'Email Verification'),
    ]

    email = models.EmailField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    otp_type = models.CharField(max_length=20, choices=OTP_TYPES)
    code = models.CharField(max_length=10)
    
    # Security fields
    attempts_count = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    is_invalidated = models.BooleanField(default=False)
    
    # Timing fields
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking fields
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    # Configuration reference
    config = models.ForeignKey(OTPConfiguration, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "OTP Request"
        verbose_name_plural = "OTP Requests"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'otp_type']),
            models.Index(fields=['code']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"OTP for {self.email} ({self.otp_type}) - {self.code}"

    def save(self, *args, **kwargs):
        if not self.pk:  # New instance
            if not self.config:
                self.config = OTPConfiguration.objects.filter(is_active=True).first()
                if not self.config:
                    # Create default config if none exists
                    self.config = OTPConfiguration.objects.create()
            
            if not self.code:
                self.code = self.generate_code()
            
            if not self.expires_at:
                self.expires_at = timezone.now() + timedelta(minutes=self.config.expiry_minutes)
        
        super().save(*args, **kwargs)

    def generate_code(self):
        """Generate secure random OTP code"""
        length = self.config.code_length if self.config else 6
        digits = string.digits
        return ''.join(secrets.choice(digits) for _ in range(length))

    def is_valid(self):
        """Check if OTP is still valid"""
        if self.is_used or self.is_expired or self.is_invalidated:
            return False
        
        if timezone.now() > self.expires_at:
            self.is_expired = True
            self.save(update_fields=['is_expired'])
            return False
        
        if self.attempts_count >= self.config.max_attempts:
            self.is_invalidated = True
            self.save(update_fields=['is_invalidated'])
            return False
        
        return True

    def verify_code(self, provided_code):
        """Verify the provided OTP code"""
        self.attempts_count += 1
        self.save(update_fields=['attempts_count'])
        
        if not self.is_valid():
            return False
        
        if self.code == provided_code:
            self.is_used = True
            self.used_at = timezone.now()
            self.save(update_fields=['is_used', 'used_at'])
            return True
        
        # Check if max attempts reached after this failed attempt
        if self.attempts_count >= self.config.max_attempts:
            self.is_invalidated = True
            self.save(update_fields=['is_invalidated'])
        
        return False

    def can_resend(self):
        """Check if OTP can be resent (cooldown period passed)"""
        if not self.config:
            return True
        
        cooldown_time = self.created_at + timedelta(minutes=self.config.resend_cooldown_minutes)
        return timezone.now() >= cooldown_time

    def get_resend_countdown(self):
        """Get remaining time for resend cooldown in seconds"""
        if not self.config:
            return 0
        
        cooldown_time = self.created_at + timedelta(minutes=self.config.resend_cooldown_minutes)
        remaining = cooldown_time - timezone.now()
        return max(0, int(remaining.total_seconds()))

    @classmethod
    def can_send_new_otp(cls, email, otp_type):
        """Check rate limiting for new OTP requests"""
        config = OTPConfiguration.objects.filter(is_active=True).first()
        if not config:
            return True, "No configuration found"
        
        # Check rate limiting
        window_start = timezone.now() - timedelta(minutes=config.rate_limit_window_minutes)
        recent_requests = cls.objects.filter(
            email=email,
            otp_type=otp_type,
            created_at__gte=window_start
        ).count()
        
        if recent_requests >= config.rate_limit_requests:
            return False, f"Rate limit exceeded. Max {config.rate_limit_requests} requests per {config.rate_limit_window_minutes} minutes."
        
        return True, "Can send OTP"

    @classmethod
    def invalidate_previous_otps(cls, email, otp_type):
        """Invalidate all previous OTPs for the same email and type"""
        cls.objects.filter(
            email=email,
            otp_type=otp_type,
            is_used=False,
            is_expired=False,
            is_invalidated=False
        ).update(is_invalidated=True)


class OTPAttemptLog(models.Model):
    """Log all OTP verification attempts for security monitoring"""
    otp_request = models.ForeignKey(OTPRequest, on_delete=models.CASCADE)
    provided_code = models.CharField(max_length=10)
    is_successful = models.BooleanField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "OTP Attempt Log"
        verbose_name_plural = "OTP Attempt Logs"
        ordering = ['-attempted_at']

    def __str__(self):
        status = "Success" if self.is_successful else "Failed"
        return f"OTP Attempt: {self.otp_request.email} - {status}"


class SecurityNotification(models.Model):
    """Track security notifications sent to users"""
    NOTIFICATION_TYPES = [
        ('password_reset_alert', 'Password Reset Alert'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('account_locked', 'Account Locked'),
        ('login_from_new_device', 'Login from New Device'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Security Notification"
        verbose_name_plural = "Security Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"Security Alert: {self.email} - {self.notification_type}"
