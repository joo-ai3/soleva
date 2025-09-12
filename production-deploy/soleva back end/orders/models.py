from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

User = get_user_model()


class Order(models.Model):
    """Main order model"""
    
    # Order identification
    order_number = models.CharField(_('order number'), max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Order status
    ORDER_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('out_for_delivery', _('Out for Delivery')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
        ('returned', _('Returned')),
    ]
    status = models.CharField(_('status'), max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    
    # Payment status
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('pending_review', _('Pending Review')),
        ('under_review', _('Under Review')),
        ('payment_approved', _('Payment Approved')),
        ('payment_rejected', _('Payment Rejected')),
        ('paid', _('Paid')),
        ('partially_paid', _('Partially Paid')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
        ('cancelled', _('Cancelled')),
    ]
    payment_status = models.CharField(_('payment status'), max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Fulfillment status
    FULFILLMENT_STATUS_CHOICES = [
        ('unfulfilled', _('Unfulfilled')),
        ('partial', _('Partial')),
        ('fulfilled', _('Fulfilled')),
    ]
    fulfillment_status = models.CharField(_('fulfillment status'), max_length=20, choices=FULFILLMENT_STATUS_CHOICES, default='unfulfilled')
    
    # Customer information
    customer_email = models.EmailField(_('customer email'))
    customer_phone = models.CharField(_('customer phone'), max_length=20)
    customer_name = models.CharField(_('customer name'), max_length=255)
    
    # Shipping address
    shipping_address_line1 = models.CharField(_('shipping address line 1'), max_length=255)
    shipping_address_line2 = models.CharField(_('shipping address line 2'), max_length=255, blank=True)
    shipping_city = models.CharField(_('shipping city'), max_length=100)
    shipping_governorate = models.CharField(_('shipping governorate'), max_length=100)
    shipping_postal_code = models.CharField(_('shipping postal code'), max_length=10, blank=True)
    shipping_phone = models.CharField(_('shipping phone'), max_length=20)
    shipping_name = models.CharField(_('shipping name'), max_length=255)
    
    # Billing address (optional, can be same as shipping)
    billing_address_line1 = models.CharField(_('billing address line 1'), max_length=255, blank=True)
    billing_address_line2 = models.CharField(_('billing address line 2'), max_length=255, blank=True)
    billing_city = models.CharField(_('billing city'), max_length=100, blank=True)
    billing_governorate = models.CharField(_('billing governorate'), max_length=100, blank=True)
    billing_postal_code = models.CharField(_('billing postal code'), max_length=10, blank=True)
    billing_phone = models.CharField(_('billing phone'), max_length=20, blank=True)
    billing_name = models.CharField(_('billing name'), max_length=255, blank=True)
    
    # Order totals
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(_('shipping cost'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(_('tax amount'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(_('discount amount'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(_('total amount'), max_digits=10, decimal_places=2)
    
    # Payment information
    payment_method = models.CharField(
        _('payment method'),
        max_length=50,
        choices=[
            ('cash_on_delivery', _('Cash on Delivery')),
            ('bank_wallet', _('Bank Wallet Payment')),
            ('e_wallet', _('E-Wallet Payment')),
            ('paymob', _('Paymob')),
            ('stripe', _('Stripe')),
        ],
        default='cash_on_delivery'
    )
    payment_reference = models.CharField(_('payment reference'), max_length=255, blank=True)
    
    # Shipping information
    shipping_method = models.CharField(_('shipping method'), max_length=100, default='standard')
    tracking_number = models.CharField(_('tracking number'), max_length=100, blank=True)
    courier_company = models.CharField(_('courier company'), max_length=100, blank=True)
    estimated_delivery_date = models.DateField(_('estimated delivery date'), blank=True, null=True)
    
    # Coupon information
    coupon_code = models.CharField(_('coupon code'), max_length=50, blank=True)
    coupon_discount = models.DecimalField(_('coupon discount'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Order notes
    customer_notes = models.TextField(_('customer notes'), blank=True)
    admin_notes = models.TextField(_('admin notes'), blank=True)
    
    # Language preference
    language = models.CharField(_('language'), max_length=10, choices=[('en', 'English'), ('ar', 'Arabic')], default='en')
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    confirmed_at = models.DateTimeField(_('confirmed at'), blank=True, null=True)
    shipped_at = models.DateTimeField(_('shipped at'), blank=True, null=True)
    delivered_at = models.DateTimeField(_('delivered at'), blank=True, null=True)
    cancelled_at = models.DateTimeField(_('cancelled at'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        db_table = 'orders'
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['customer_email']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_order_number(cls):
        """Generate unique order number"""
        import datetime
        today = datetime.date.today()
        prefix = f"SOL{today.strftime('%y%m%d')}"
        
        # Find the last order number for today
        last_order = cls.objects.filter(
            order_number__startswith=prefix
        ).order_by('order_number').last()
        
        if last_order:
            last_number = int(last_order.order_number[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"
    
    @property
    def full_shipping_address(self):
        """Get formatted shipping address"""
        parts = [self.shipping_address_line1]
        if self.shipping_address_line2:
            parts.append(self.shipping_address_line2)
        parts.extend([self.shipping_city, self.shipping_governorate])
        if self.shipping_postal_code:
            parts.append(self.shipping_postal_code)
        return ", ".join(parts)
    
    @property
    def is_paid(self):
        """Check if order is paid"""
        return self.payment_status in ['paid', 'payment_approved']
    
    @property
    def requires_payment_proof(self):
        """Check if order requires payment proof upload"""
        return self.payment_method in ['bank_wallet', 'e_wallet']
    
    @property
    def has_payment_proof(self):
        """Check if order has payment proof uploaded"""
        return self.payment_proofs.exists()
    
    @property
    def payment_proof_status(self):
        """Get the latest payment proof verification status"""
        latest_proof = self.payment_proofs.order_by('-created_at').first()
        return latest_proof.verification_status if latest_proof else None
    
    @property
    def can_be_cancelled(self):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'confirmed'] and self.payment_status not in ['payment_approved', 'paid']


class OrderItem(models.Model):
    """Order line items"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    
    # Product information (stored at time of order)
    product_id = models.PositiveIntegerField(_('product ID'))
    product_name = models.CharField(_('product name'), max_length=255)
    product_sku = models.CharField(_('product SKU'), max_length=100)
    product_image = models.URLField(_('product image'), blank=True)
    
    # Variant information (if applicable)
    variant_id = models.PositiveIntegerField(_('variant ID'), blank=True, null=True)
    variant_sku = models.CharField(_('variant SKU'), max_length=100, blank=True)
    variant_attributes = models.JSONField(_('variant attributes'), default=dict, blank=True)
    
    # Pricing and quantity
    unit_price = models.DecimalField(_('unit price'), max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(_('quantity'))
    total_price = models.DecimalField(_('total price'), max_digits=10, decimal_places=2)
    
    # Fulfillment
    quantity_fulfilled = models.PositiveIntegerField(_('quantity fulfilled'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        db_table = 'order_items'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product_id']),
            models.Index(fields=['variant_id']),
        ]
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
    
    @property
    def is_fulfilled(self):
        """Check if item is fully fulfilled"""
        return self.quantity_fulfilled >= self.quantity
    
    @property
    def pending_quantity(self):
        """Get pending fulfillment quantity"""
        return self.quantity - self.quantity_fulfilled


class OrderStatusHistory(models.Model):
    """Track order status changes"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    previous_status = models.CharField(_('previous status'), max_length=20, blank=True)
    new_status = models.CharField(_('new status'), max_length=20)
    comment = models.TextField(_('comment'), blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Order Status History')
        verbose_name_plural = _('Order Status Histories')
        db_table = 'order_status_history'
        indexes = [
            models.Index(fields=['order', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.order.order_number}: {self.previous_status} → {self.new_status}"


class OrderPayment(models.Model):
    """Track order payments"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    payment_method = models.CharField(_('payment method'), max_length=50)
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=3, default='EGP')
    
    # Payment gateway information
    gateway_transaction_id = models.CharField(_('gateway transaction ID'), max_length=255, blank=True)
    gateway_reference = models.CharField(_('gateway reference'), max_length=255, blank=True)
    gateway_response = models.JSONField(_('gateway response'), default=dict, blank=True)
    
    # Payment status
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    ]
    status = models.CharField(_('status'), max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    processed_at = models.DateTimeField(_('processed at'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Order Payment')
        verbose_name_plural = _('Order Payments')
        db_table = 'order_payments'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['gateway_transaction_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.order.order_number} - {self.payment_method} - {self.amount}"


class OrderShipment(models.Model):
    """Track order shipments"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipments')
    
    # Shipment details
    tracking_number = models.CharField(_('tracking number'), max_length=100)
    courier_company = models.CharField(_('courier company'), max_length=100)
    shipping_cost = models.DecimalField(_('shipping cost'), max_digits=10, decimal_places=2)
    
    # Shipment status
    SHIPMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('picked_up', _('Picked Up')),
        ('in_transit', _('In Transit')),
        ('out_for_delivery', _('Out for Delivery')),
        ('delivered', _('Delivered')),
        ('failed_delivery', _('Failed Delivery')),
        ('returned', _('Returned')),
    ]
    status = models.CharField(_('status'), max_length=20, choices=SHIPMENT_STATUS_CHOICES, default='pending')
    
    # Tracking information
    tracking_url = models.URLField(_('tracking URL'), blank=True)
    estimated_delivery = models.DateTimeField(_('estimated delivery'), blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    shipped_at = models.DateTimeField(_('shipped at'), blank=True, null=True)
    delivered_at = models.DateTimeField(_('delivered at'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Order Shipment')
        verbose_name_plural = _('Order Shipments')
        db_table = 'order_shipments'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['tracking_number']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.order.order_number} - {self.tracking_number}"


class OrderRefund(models.Model):
    """Track order refunds"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds')
    
    # Refund details
    amount = models.DecimalField(_('refund amount'), max_digits=10, decimal_places=2)
    reason = models.TextField(_('refund reason'))
    
    # Refund status
    REFUND_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('processed', _('Processed')),
        ('completed', _('Completed')),
        ('rejected', _('Rejected')),
    ]
    status = models.CharField(_('status'), max_length=20, choices=REFUND_STATUS_CHOICES, default='pending')
    
    # Processing information
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    gateway_refund_id = models.CharField(_('gateway refund ID'), max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    processed_at = models.DateTimeField(_('processed at'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Order Refund')
        verbose_name_plural = _('Order Refunds')
        db_table = 'order_refunds'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.order.order_number} - Refund {self.amount}"


class PaymentProof(models.Model):
    """Payment proof attachments for bank wallet and e-wallet payments"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment_proofs')
    
    # File information
    image = models.ImageField(_('payment proof image'), upload_to='payment_proofs/%Y/%m/')
    original_filename = models.CharField(_('original filename'), max_length=255)
    file_size = models.PositiveIntegerField(_('file size (bytes)'))
    
    # Upload details
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    upload_ip = models.GenericIPAddressField(_('upload IP'), blank=True, null=True)
    
    # Verification status
    VERIFICATION_STATUS_CHOICES = [
        ('pending', _('Pending Verification')),
        ('verified', _('Verified')),
        ('rejected', _('Rejected')),
        ('needs_clarification', _('Needs Clarification')),
    ]
    verification_status = models.CharField(
        _('verification status'), 
        max_length=20, 
        choices=VERIFICATION_STATUS_CHOICES, 
        default='pending'
    )
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_payment_proofs'
    )
    verification_notes = models.TextField(_('verification notes'), blank=True)
    verified_at = models.DateTimeField(_('verified at'), blank=True, null=True)
    
    # Metadata
    description = models.TextField(_('description'), blank=True, help_text=_('Customer description of the payment'))
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Payment Proof')
        verbose_name_plural = _('Payment Proofs')
        db_table = 'order_payment_proofs'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['verification_status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - Payment Proof ({self.verification_status})"
    
    def save(self, *args, **kwargs):
        if self.image:
            self.file_size = self.image.size
            if not self.original_filename:
                self.original_filename = self.image.name
        super().save(*args, **kwargs)
    
    @property
    def is_verified(self):
        """Check if payment proof is verified"""
        return self.verification_status == 'verified'
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2) if self.file_size else 0
