from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationTemplate(models.Model):
    """Email/SMS notification templates"""
    
    # Template identification
    code = models.CharField(_('template code'), max_length=100, unique=True)
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    
    # Template type
    TEMPLATE_TYPE_CHOICES = [
        ('email', _('Email')),
        ('sms', _('SMS')),
        ('push', _('Push Notification')),
    ]
    template_type = models.CharField(_('template type'), max_length=20, choices=TEMPLATE_TYPE_CHOICES)
    
    # Email specific fields
    subject_en = models.CharField(_('subject (English)'), max_length=200, blank=True)
    subject_ar = models.CharField(_('subject (Arabic)'), max_length=200, blank=True)
    
    # Message content
    content_en = models.TextField(_('content (English)'))
    content_ar = models.TextField(_('content (Arabic)'))
    
    # HTML content for emails
    html_content_en = models.TextField(_('HTML content (English)'), blank=True)
    html_content_ar = models.TextField(_('HTML content (Arabic)'), blank=True)
    
    # Status
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Notification Template')
        verbose_name_plural = _('Notification Templates')
        db_table = 'notification_templates'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['template_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"


class Notification(models.Model):
    """Individual notifications sent to users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Notification type
    NOTIFICATION_TYPE_CHOICES = [
        ('order_confirmation', _('Order Confirmation')),
        ('order_shipped', _('Order Shipped')),
        ('order_delivered', _('Order Delivered')),
        ('order_cancelled', _('Order Cancelled')),
        ('payment_received', _('Payment Received')),
        ('payment_failed', _('Payment Failed')),
        ('account_created', _('Account Created')),
        ('password_reset', _('Password Reset')),
        ('promotional', _('Promotional')),
        ('abandoned_cart', _('Abandoned Cart')),
        ('back_in_stock', _('Back in Stock')),
        ('price_drop', _('Price Drop')),
        ('system', _('System')),
    ]
    notification_type = models.CharField(_('notification type'), max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    
    # Content
    title = models.CharField(_('title'), max_length=200)
    message = models.TextField(_('message'))
    
    # Delivery channels
    CHANNEL_CHOICES = [
        ('email', _('Email')),
        ('sms', _('SMS')),
        ('push', _('Push Notification')),
        ('in_app', _('In-App Notification')),
    ]
    channel = models.CharField(_('channel'), max_length=20, choices=CHANNEL_CHOICES)
    
    # Delivery status
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('delivered', _('Delivered')),
        ('failed', _('Failed')),
        ('read', _('Read')),
    ]
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Delivery details
    recipient_email = models.EmailField(_('recipient email'), blank=True)
    recipient_phone = models.CharField(_('recipient phone'), max_length=20, blank=True)
    
    # Metadata
    context_data = models.JSONField(_('context data'), default=dict, blank=True)
    error_message = models.TextField(_('error message'), blank=True)
    
    # Related objects
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    sent_at = models.DateTimeField(_('sent at'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('delivered at'), null=True, blank=True)
    read_at = models.DateTimeField(_('read at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['channel']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    @property
    def is_read(self):
        return self.read_at is not None
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.read_at:
            from django.utils import timezone
            self.read_at = timezone.now()
            self.status = 'read'
            self.save(update_fields=['read_at', 'status'])


class EmailQueue(models.Model):
    """Queue for email sending"""
    
    # Recipient information
    to_email = models.EmailField(_('to email'))
    to_name = models.CharField(_('to name'), max_length=200, blank=True)
    
    # Email content
    subject = models.CharField(_('subject'), max_length=200)
    message = models.TextField(_('message'))
    html_message = models.TextField(_('HTML message'), blank=True)
    
    # Sender information
    from_email = models.EmailField(_('from email'), blank=True)
    from_name = models.CharField(_('from name'), max_length=200, blank=True)
    
    # Priority
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('normal', _('Normal')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]
    priority = models.CharField(_('priority'), max_length=20, choices=PRIORITY_CHOICES, default='normal')
    
    # Status
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ]
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Retry logic
    retry_count = models.PositiveIntegerField(_('retry count'), default=0)
    max_retries = models.PositiveIntegerField(_('max retries'), default=3)
    
    # Metadata
    context_data = models.JSONField(_('context data'), default=dict, blank=True)
    error_message = models.TextField(_('error message'), blank=True)
    
    # Related objects
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    scheduled_at = models.DateTimeField(_('scheduled at'), null=True, blank=True)
    sent_at = models.DateTimeField(_('sent at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Email Queue')
        verbose_name_plural = _('Email Queue')
        db_table = 'email_queue'
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['scheduled_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.subject} - {self.to_email}"


class SMSQueue(models.Model):
    """Queue for SMS sending"""
    
    # Recipient information
    to_phone = models.CharField(_('to phone'), max_length=20)
    
    # Message content
    message = models.TextField(_('message'))
    
    # Priority
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('normal', _('Normal')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]
    priority = models.CharField(_('priority'), max_length=20, choices=PRIORITY_CHOICES, default='normal')
    
    # Status
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ]
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Retry logic
    retry_count = models.PositiveIntegerField(_('retry count'), default=0)
    max_retries = models.PositiveIntegerField(_('max retries'), default=3)
    
    # Provider information
    provider = models.CharField(_('SMS provider'), max_length=50, default='default')
    provider_message_id = models.CharField(_('provider message ID'), max_length=100, blank=True)
    
    # Metadata
    context_data = models.JSONField(_('context data'), default=dict, blank=True)
    error_message = models.TextField(_('error message'), blank=True)
    
    # Related objects
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    scheduled_at = models.DateTimeField(_('scheduled at'), null=True, blank=True)
    sent_at = models.DateTimeField(_('sent at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('SMS Queue')
        verbose_name_plural = _('SMS Queue')
        db_table = 'sms_queue'
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['scheduled_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"SMS to {self.to_phone}"


class PushNotificationDevice(models.Model):
    """User devices for push notifications"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_devices')
    
    # Device information
    device_token = models.TextField(_('device token'), unique=True)
    device_type = models.CharField(
        _('device type'),
        max_length=20,
        choices=[
            ('ios', _('iOS')),
            ('android', _('Android')),
            ('web', _('Web')),
        ]
    )
    device_name = models.CharField(_('device name'), max_length=200, blank=True)
    
    # Status
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    last_used_at = models.DateTimeField(_('last used at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Push Notification Device')
        verbose_name_plural = _('Push Notification Devices')
        db_table = 'push_notification_devices'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['device_token']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.device_type}"
