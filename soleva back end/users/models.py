from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    """Custom user manager to handle create_superuser with email as USERNAME_FIELD"""

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, email, password, **extra_fields)

    def _create_user(self, email, username, password, **extra_fields):
        """Create and save a user with the given email, username and password."""
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)

        # Set username to email if not provided (for compatibility)
        if not username:
            username = email

        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""

    email = models.EmailField(_('email address'), unique=True)

    # Use custom manager
    objects = CustomUserManager()
    phone_number = PhoneNumberField(_('phone number'), blank=True, null=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    gender = models.CharField(
        _('gender'),
        max_length=10,
        choices=[
            ('male', _('Male')),
            ('female', _('Female')),
            ('other', _('Other')),
        ],
        blank=True,
        null=True
    )
    
    # Profile settings
    language_preference = models.CharField(
        _('language preference'),
        max_length=10,
        choices=[
            ('en', _('English')),
            ('ar', _('Arabic')),
        ],
        default='en'
    )
    
    # Marketing preferences
    email_notifications = models.BooleanField(_('email notifications'), default=True)
    sms_notifications = models.BooleanField(_('SMS notifications'), default=True)
    push_notifications = models.BooleanField(_('push notifications'), default=True)
    
    # Account status
    is_verified = models.BooleanField(_('is verified'), default=False)
    verification_code = models.CharField(_('verification code'), max_length=6, blank=True, null=True)
    verification_code_expires = models.DateTimeField(_('verification code expires'), blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    last_login_ip = models.GenericIPAddressField(_('last login IP'), blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Address(models.Model):
    """User addresses for shipping"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    
    # Address details
    full_name = models.CharField(_('full name'), max_length=255)
    phone_number = PhoneNumberField(_('phone number'))
    
    # Egypt-specific address fields
    governorate = models.CharField(_('governorate'), max_length=100)
    city = models.CharField(_('city/markaz'), max_length=100)
    area = models.CharField(_('area/district'), max_length=100, blank=True)
    street_address = models.TextField(_('street address'))
    building_number = models.CharField(_('building number'), max_length=50, blank=True)
    apartment_number = models.CharField(_('apartment number'), max_length=50, blank=True)
    floor_number = models.CharField(_('floor number'), max_length=10, blank=True)
    landmark = models.CharField(_('landmark'), max_length=255, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=10, blank=True)
    
    # Address type and status
    address_type = models.CharField(
        _('address type'),
        max_length=20,
        choices=[
            ('home', _('Home')),
            ('work', _('Work')),
            ('other', _('Other')),
        ],
        default='home'
    )
    is_default = models.BooleanField(_('is default'), default=False)
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Coordinates for delivery optimization (optional)
    latitude = models.DecimalField(_('latitude'), max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(_('longitude'), max_digits=11, decimal_places=8, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
        db_table = 'user_addresses'
        indexes = [
            models.Index(fields=['user', 'is_default']),
            models.Index(fields=['governorate', 'city']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_default=True),
                name='unique_default_address_per_user'
            ),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.governorate}, {self.city}"
    
    def save(self, *args, **kwargs):
        # Ensure only one default address per user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
    
    @property
    def full_address(self):
        """Return formatted full address"""
        parts = []
        if self.street_address:
            parts.append(self.street_address)
        if self.building_number:
            parts.append(f"Building {self.building_number}")
        if self.apartment_number:
            parts.append(f"Apt {self.apartment_number}")
        if self.floor_number:
            parts.append(f"Floor {self.floor_number}")
        if self.area:
            parts.append(self.area)
        parts.extend([self.city, self.governorate])
        if self.postal_code:
            parts.append(self.postal_code)
        
        return ", ".join(parts)


class UserSession(models.Model):
    """Track user sessions for security"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(_('session key'), max_length=40, unique=True)
    device_info = models.TextField(_('device info'), blank=True)
    ip_address = models.GenericIPAddressField(_('IP address'))
    user_agent = models.TextField(_('user agent'), blank=True)
    
    # Location info (optional)
    country = models.CharField(_('country'), max_length=100, blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    
    # Session status
    is_active = models.BooleanField(_('is active'), default=True)
    last_activity = models.DateTimeField(_('last activity'), auto_now=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    expires_at = models.DateTimeField(_('expires at'))
    
    class Meta:
        verbose_name = _('User Session')
        verbose_name_plural = _('User Sessions')
        db_table = 'user_sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.ip_address}"
