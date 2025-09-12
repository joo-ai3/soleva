from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

User = get_user_model()


class PaymentMethod(models.Model):
    """Payment methods configuration"""
    
    name = models.CharField(_('name'), max_length=100, unique=True)
    code = models.CharField(_('code'), max_length=50, unique=True)
    description = models.TextField(_('description'), blank=True)
    
    # Configuration
    is_active = models.BooleanField(_('is active'), default=True)
    requires_gateway = models.BooleanField(_('requires gateway'), default=True)
    min_amount = models.DecimalField(_('minimum amount'), max_digits=10, decimal_places=2, default=Decimal('1.00'))
    max_amount = models.DecimalField(_('maximum amount'), max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Fees
    fixed_fee = models.DecimalField(_('fixed fee'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    percentage_fee = models.DecimalField(_('percentage fee'), max_digits=5, decimal_places=4, default=Decimal('0.0000'))
    
    # Display settings
    display_name_en = models.CharField(_('display name (English)'), max_length=100)
    display_name_ar = models.CharField(_('display name (Arabic)'), max_length=100)
    icon = models.CharField(_('icon class'), max_length=100, blank=True)
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        db_table = 'payment_methods'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    def calculate_fees(self, amount):
        """Calculate payment fees"""
        fees = self.fixed_fee + (amount * self.percentage_fee / 100)
        return fees


class PaymentTransaction(models.Model):
    """Payment transactions"""
    
    # Transaction identification
    transaction_id = models.CharField(_('transaction ID'), max_length=100, unique=True)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payment_transactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_transactions')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    
    # Amount details
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=3, default='EGP')
    fees = models.DecimalField(_('fees'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    net_amount = models.DecimalField(_('net amount'), max_digits=10, decimal_places=2)
    
    # Transaction status
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
        ('partially_refunded', _('Partially Refunded')),
    ]
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Gateway information
    gateway_name = models.CharField(_('gateway name'), max_length=50)
    gateway_transaction_id = models.CharField(_('gateway transaction ID'), max_length=255, blank=True)
    gateway_reference = models.CharField(_('gateway reference'), max_length=255, blank=True)
    gateway_response = models.JSONField(_('gateway response'), default=dict, blank=True)
    gateway_webhook_data = models.JSONField(_('gateway webhook data'), default=dict, blank=True)
    
    # Customer information
    customer_email = models.EmailField(_('customer email'))
    customer_phone = models.CharField(_('customer phone'), max_length=20, blank=True)
    customer_name = models.CharField(_('customer name'), max_length=255)
    
    # Billing information
    billing_address = models.JSONField(_('billing address'), default=dict, blank=True)
    
    # Transaction metadata
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    failure_reason = models.TextField(_('failure reason'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    processed_at = models.DateTimeField(_('processed at'), blank=True, null=True)
    completed_at = models.DateTimeField(_('completed at'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Payment Transaction')
        verbose_name_plural = _('Payment Transactions')
        db_table = 'payment_transactions'
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['order', 'status']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['gateway_transaction_id']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        
        # Calculate net amount
        self.net_amount = self.amount - self.fees
        
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_transaction_id(cls):
        """Generate unique transaction ID"""
        import datetime
        today = datetime.date.today()
        prefix = f"TXN{today.strftime('%y%m%d')}"
        
        # Find the last transaction for today
        last_transaction = cls.objects.filter(
            transaction_id__startswith=prefix
        ).order_by('transaction_id').last()
        
        if last_transaction:
            last_number = int(last_transaction.transaction_id[-6:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:06d}"
    
    @property
    def is_successful(self):
        """Check if transaction is successful"""
        return self.status == 'completed'
    
    @property
    def can_be_refunded(self):
        """Check if transaction can be refunded"""
        return self.status == 'completed' and self.gateway_name != 'cash_on_delivery'


class PaymentRefund(models.Model):
    """Payment refunds"""
    
    # Refund identification
    refund_id = models.CharField(_('refund ID'), max_length=100, unique=True)
    transaction = models.ForeignKey(PaymentTransaction, on_delete=models.CASCADE, related_name='refunds')
    
    # Refund details
    amount = models.DecimalField(_('refund amount'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=3, default='EGP')
    reason = models.TextField(_('refund reason'))
    
    # Refund status
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ]
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Gateway information
    gateway_refund_id = models.CharField(_('gateway refund ID'), max_length=255, blank=True)
    gateway_response = models.JSONField(_('gateway response'), default=dict, blank=True)
    
    # Processing information
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refunds')
    failure_reason = models.TextField(_('failure reason'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    processed_at = models.DateTimeField(_('processed at'), blank=True, null=True)
    completed_at = models.DateTimeField(_('completed at'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Payment Refund')
        verbose_name_plural = _('Payment Refunds')
        db_table = 'payment_refunds'
        indexes = [
            models.Index(fields=['refund_id']),
            models.Index(fields=['transaction', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Refund {self.refund_id} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        if not self.refund_id:
            self.refund_id = self.generate_refund_id()
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_refund_id(cls):
        """Generate unique refund ID"""
        import datetime
        today = datetime.date.today()
        prefix = f"REF{today.strftime('%y%m%d')}"
        
        # Find the last refund for today
        last_refund = cls.objects.filter(
            refund_id__startswith=prefix
        ).order_by('refund_id').last()
        
        if last_refund:
            last_number = int(last_refund.refund_id[-6:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:06d}"


class PaymentWebhook(models.Model):
    """Payment gateway webhooks log"""
    
    # Webhook identification
    webhook_id = models.CharField(_('webhook ID'), max_length=100, unique=True)
    gateway_name = models.CharField(_('gateway name'), max_length=50)
    event_type = models.CharField(_('event type'), max_length=100)
    
    # Webhook data
    raw_data = models.JSONField(_('raw data'), default=dict)
    headers = models.JSONField(_('headers'), default=dict)
    
    # Processing status
    is_processed = models.BooleanField(_('is processed'), default=False)
    processing_attempts = models.PositiveIntegerField(_('processing attempts'), default=0)
    last_processing_error = models.TextField(_('last processing error'), blank=True)
    
    # Related transaction (if found)
    transaction = models.ForeignKey(
        PaymentTransaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='webhooks'
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    processed_at = models.DateTimeField(_('processed at'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Payment Webhook')
        verbose_name_plural = _('Payment Webhooks')
        db_table = 'payment_webhooks'
        indexes = [
            models.Index(fields=['gateway_name', 'event_type']),
            models.Index(fields=['is_processed', 'created_at']),
            models.Index(fields=['transaction']),
        ]
    
    def __str__(self):
        return f"Webhook {self.webhook_id} - {self.gateway_name} - {self.event_type}"
    
    def save(self, *args, **kwargs):
        if not self.webhook_id:
            self.webhook_id = str(uuid.uuid4())
        super().save(*args, **kwargs)
