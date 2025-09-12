from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import string
import random

User = get_user_model()


class Coupon(models.Model):
    """Discount coupons"""
    
    # Basic information
    code = models.CharField(_('coupon code'), max_length=50, unique=True)
    name_en = models.CharField(_('name (English)'), max_length=100)
    name_ar = models.CharField(_('name (Arabic)'), max_length=100)
    description_en = models.TextField(_('description (English)'), blank=True)
    description_ar = models.TextField(_('description (Arabic)'), blank=True)
    
    # Discount type and value
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', _('Percentage')),
        ('fixed_amount', _('Fixed Amount')),
    ]
    discount_type = models.CharField(_('discount type'), max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(_('discount value'), max_digits=10, decimal_places=2)
    
    # Usage restrictions
    minimum_order_amount = models.DecimalField(_('minimum order amount'), max_digits=10, decimal_places=2, default=Decimal('0.00'), blank=True, null=True)
    max_discount_amount = models.DecimalField(_('maximum discount amount'), max_digits=10, decimal_places=2, blank=True, null=True)
    free_shipping = models.BooleanField(_('free shipping'), default=False)
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(_('usage limit'), blank=True, null=True, help_text=_('Total number of times this coupon can be used'))
    usage_limit_per_customer = models.PositiveIntegerField(_('usage limit per customer'), blank=True, null=True)
    used_count = models.PositiveIntegerField(_('used count'), default=0)
    
    # Validity period
    valid_from = models.DateField(_('valid from'))
    valid_until = models.DateField(_('valid until'), blank=True, null=True)
    
    # Customer restrictions
    specific_customers = models.ManyToManyField(User, blank=True, related_name='available_coupons', help_text=_('Leave empty for all customers'))
    first_time_customers_only = models.BooleanField(_('first time customers only'), default=False)
    
    # Product/Category restrictions
    applicable_categories = models.ManyToManyField('products.Category', blank=True, related_name='coupons')
    applicable_products = models.ManyToManyField('products.Product', blank=True, related_name='coupons')
    exclude_sale_items = models.BooleanField(_('exclude sale items'), default=False)
    
    # Status
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')
        db_table = 'coupons'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'valid_from', 'valid_until']),
            models.Index(fields=['discount_type']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name_en}"
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_code(cls, length=8):
        """Generate random coupon code"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if not cls.objects.filter(code=code).exists():
                return code
    
    @property
    def is_valid(self):
        """Check if coupon is currently valid"""
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.is_active and
            self.valid_from <= today and
            (self.valid_until is None or today <= self.valid_until) and
            (self.usage_limit is None or self.used_count < self.usage_limit)
        )
    
    def can_be_used_by_customer(self, user, order_total=None):
        """Check if coupon can be used by specific customer"""
        if not self.is_valid:
            return False, _('Coupon is not valid')
        
        # Check minimum order amount
        if order_total and self.minimum_order_amount and order_total < self.minimum_order_amount:
            return False, _('Minimum order amount not met')
        
        # Check customer restrictions
        if self.specific_customers.exists() and user not in self.specific_customers.all():
            return False, _('Coupon not available for this customer')
        
        # Check first time customer restriction
        if self.first_time_customers_only and user.orders.exists():
            return False, _('Coupon only for first-time customers')
        
        # Check usage limit per customer
        if self.usage_limit_per_customer:
            customer_usage = CouponUsage.objects.filter(coupon=self, user=user).count()
            if customer_usage >= self.usage_limit_per_customer:
                return False, _('Usage limit per customer exceeded')
        
        return True, _('Coupon can be used')
    
    def calculate_discount(self, order_total, shipping_cost=0):
        """Calculate discount amount for given order total"""
        discount = Decimal('0.00')
        
        if self.discount_type == 'percentage':
            discount = order_total * (self.discount_value / 100)
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
        elif self.discount_type == 'fixed_amount':
            discount = min(self.discount_value, order_total)
        
        return discount


class CouponUsage(models.Model):
    """Track coupon usage"""
    
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usage_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usage', blank=True, null=True)
    order_id = models.CharField(_('order ID'), max_length=50, blank=True, null=True)
    
    # Usage details
    discount_amount = models.DecimalField(_('discount amount'), max_digits=10, decimal_places=2)
    order_total = models.DecimalField(_('order total'), max_digits=10, decimal_places=2)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Coupon Usage')
        verbose_name_plural = _('Coupon Usages')
        db_table = 'coupon_usage'
        indexes = [
            models.Index(fields=['coupon', 'user']),
            models.Index(fields=['created_at']),
            models.Index(fields=['order_id']),
        ]
    
    def __str__(self):
        user_email = self.user.email if self.user else 'Guest'
        return f"{self.coupon.code} - {user_email} - {self.order_id or 'N/A'}"


class CouponCategory(models.Model):
    """Coupon categories for organization"""
    
    name = models.CharField(_('name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    color = models.CharField(_('color'), max_length=7, default='#007bff')  # Hex color
    
    # Status
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Coupon Category')
        verbose_name_plural = _('Coupon Categories')
        db_table = 'coupon_categories'
    
    def __str__(self):
        return self.name
