from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class FlashSale(models.Model):
    """Flash sale campaigns"""
    
    # Basic information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_en = models.CharField(_('name (English)'), max_length=200)
    name_ar = models.CharField(_('name (Arabic)'), max_length=200)
    description_en = models.TextField(_('description (English)'), blank=True)
    description_ar = models.TextField(_('description (Arabic)'), blank=True)
    
    # Timing
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'))
    
    # Display settings
    banner_image = models.ImageField(_('banner image'), upload_to='flash_sales/banners/', blank=True, null=True)
    banner_color = models.CharField(_('banner color'), max_length=7, default='#ff4444')  # Hex color
    text_color = models.CharField(_('text color'), max_length=7, default='#ffffff')  # Hex color
    display_priority = models.PositiveIntegerField(_('display priority'), default=0, help_text=_('Higher numbers appear first'))
    
    # Settings
    is_active = models.BooleanField(_('is active'), default=True)
    show_countdown = models.BooleanField(_('show countdown timer'), default=True)
    
    # Restrictions
    max_uses_per_customer = models.PositiveIntegerField(_('max uses per customer'), blank=True, null=True)
    total_usage_limit = models.PositiveIntegerField(_('total usage limit'), blank=True, null=True)
    current_usage_count = models.PositiveIntegerField(_('current usage count'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Flash Sale')
        verbose_name_plural = _('Flash Sales')
        db_table = 'offers_flash_sales'
        ordering = ['-display_priority', '-start_time']
        indexes = [
            models.Index(fields=['is_active', 'start_time', 'end_time']),
            models.Index(fields=['display_priority']),
        ]
    
    def __str__(self):
        return self.name_en
    
    @property
    def is_running(self):
        """Check if flash sale is currently running"""
        now = timezone.now()
        return (
            self.is_active and
            self.start_time <= now <= self.end_time and
            (self.total_usage_limit is None or self.current_usage_count < self.total_usage_limit)
        )
    
    @property
    def is_upcoming(self):
        """Check if flash sale is upcoming"""
        return self.is_active and timezone.now() < self.start_time
    
    @property
    def is_expired(self):
        """Check if flash sale has expired"""
        return timezone.now() > self.end_time
    
    @property
    def time_remaining(self):
        """Get time remaining in seconds"""
        if self.is_expired:
            return 0
        return int((self.end_time - timezone.now()).total_seconds())


class SpecialOffer(models.Model):
    """Special product offers like Buy 2 Get 1 Free, etc."""
    
    OFFER_TYPE_CHOICES = [
        ('buy_x_get_y_free', _('Buy X Get Y Free')),
        ('buy_x_get_discount', _('Buy X Get Discount')),
        ('buy_x_free_shipping', _('Buy X Get Free Shipping')),
        ('bundle_discount', _('Bundle Discount')),
    ]
    
    # Basic information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_en = models.CharField(_('name (English)'), max_length=200)
    name_ar = models.CharField(_('name (Arabic)'), max_length=200)
    description_en = models.TextField(_('description (English)'), blank=True)
    description_ar = models.TextField(_('description (Arabic)'), blank=True)
    
    # Offer type and configuration
    offer_type = models.CharField(_('offer type'), max_length=20, choices=OFFER_TYPE_CHOICES)
    
    # Buy X Get Y Free configuration
    buy_quantity = models.PositiveIntegerField(_('buy quantity'), default=2, help_text=_('Minimum quantity to buy'))
    free_quantity = models.PositiveIntegerField(_('free quantity'), default=1, help_text=_('Number of free items'))
    
    # Discount configuration
    discount_type = models.CharField(_('discount type'), max_length=20, choices=[
        ('percentage', _('Percentage')),
        ('fixed_amount', _('Fixed Amount')),
    ], default='percentage')
    discount_value = models.DecimalField(_('discount value'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Product restrictions
    applicable_products = models.ManyToManyField('products.Product', related_name='special_offers', blank=True)
    applicable_categories = models.ManyToManyField('products.Category', related_name='special_offers', blank=True)
    
    # Timing
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'), blank=True, null=True)
    
    # Usage restrictions
    max_uses_per_customer = models.PositiveIntegerField(_('max uses per customer'), blank=True, null=True)
    total_usage_limit = models.PositiveIntegerField(_('total usage limit'), blank=True, null=True)
    current_usage_count = models.PositiveIntegerField(_('current usage count'), default=0)
    minimum_order_amount = models.DecimalField(_('minimum order amount'), max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Display settings
    button_text_en = models.CharField(_('button text (English)'), max_length=100, default='Activate Offer')
    button_text_ar = models.CharField(_('button text (Arabic)'), max_length=100, default='تفعيل العرض')
    button_color = models.CharField(_('button color'), max_length=7, default='#ff4444')
    highlight_color = models.CharField(_('highlight color'), max_length=7, default='#ffeb3b')
    
    # Settings
    is_active = models.BooleanField(_('is active'), default=True)
    show_on_product_page = models.BooleanField(_('show on product page'), default=True)
    show_timer = models.BooleanField(_('show countdown timer'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Special Offer')
        verbose_name_plural = _('Special Offers')
        db_table = 'offers_special_offers'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['is_active', 'start_time', 'end_time']),
            models.Index(fields=['offer_type']),
        ]
    
    def __str__(self):
        return self.name_en
    
    @property
    def is_running(self):
        """Check if offer is currently running"""
        now = timezone.now()
        return (
            self.is_active and
            self.start_time <= now and
            (self.end_time is None or now <= self.end_time) and
            (self.total_usage_limit is None or self.current_usage_count < self.total_usage_limit)
        )
    
    @property
    def is_upcoming(self):
        """Check if offer is upcoming"""
        return self.is_active and timezone.now() < self.start_time
    
    @property
    def is_expired(self):
        """Check if offer has expired"""
        return self.end_time and timezone.now() > self.end_time
    
    @property
    def time_remaining(self):
        """Get time remaining in seconds"""
        if not self.end_time or self.is_expired:
            return None
        return int((self.end_time - timezone.now()).total_seconds())
    
    def can_be_used_by_customer(self, user, current_usage_count=None):
        """Check if offer can be used by specific customer"""
        if not self.is_running:
            return False, _('Offer is not active')
        
        # Check customer usage limit
        if self.max_uses_per_customer and current_usage_count:
            if current_usage_count >= self.max_uses_per_customer:
                return False, _('Usage limit per customer exceeded')
        
        return True, _('Offer can be used')
    
    def calculate_discount(self, cart_items, cart_total):
        """Calculate discount based on offer type and cart contents"""
        if not self.is_running:
            return {
                'discount_amount': Decimal('0.00'),
                'free_items': [],
                'free_shipping': False,
                'description': ''
            }
        
        # Filter applicable items
        applicable_items = []
        for item in cart_items:
            if self.is_product_applicable(item['product_id']):
                applicable_items.append(item)
        
        if not applicable_items:
            return {
                'discount_amount': Decimal('0.00'),
                'free_items': [],
                'free_shipping': False,
                'description': 'No applicable items in cart'
            }
        
        # Calculate based on offer type
        if self.offer_type == 'buy_x_get_y_free':
            return self._calculate_buy_x_get_y_free(applicable_items)
        elif self.offer_type == 'buy_x_get_discount':
            return self._calculate_buy_x_get_discount(applicable_items, cart_total)
        elif self.offer_type == 'buy_x_free_shipping':
            return self._calculate_free_shipping(applicable_items)
        elif self.offer_type == 'bundle_discount':
            return self._calculate_bundle_discount(applicable_items, cart_total)
        
        return {
            'discount_amount': Decimal('0.00'),
            'free_items': [],
            'free_shipping': False,
            'description': 'Unknown offer type'
        }
    
    def is_product_applicable(self, product_id):
        """Check if a product is applicable for this offer"""
        if self.applicable_products.exists():
            return self.applicable_products.filter(id=product_id).exists()
        
        if self.applicable_categories.exists():
            from products.models import Product
            try:
                product = Product.objects.get(id=product_id)
                return self.applicable_categories.filter(id=product.category_id).exists()
            except Product.DoesNotExist:
                return False
        
        return True  # If no restrictions, apply to all products
    
    def _calculate_buy_x_get_y_free(self, applicable_items):
        """Calculate Buy X Get Y Free discount"""
        total_qty = sum(item['quantity'] for item in applicable_items)
        
        if total_qty < self.buy_quantity:
            return {
                'discount_amount': Decimal('0.00'),
                'free_items': [],
                'free_shipping': False,
                'description': f'Need {self.buy_quantity - total_qty} more items'
            }
        
        # Calculate free items
        free_sets = total_qty // self.buy_quantity
        total_free_items = free_sets * self.free_quantity
        
        # Sort items by price (lowest first for free items)
        sorted_items = sorted(applicable_items, key=lambda x: x['price'])
        
        free_items = []
        remaining_free = total_free_items
        
        for item in sorted_items:
            if remaining_free <= 0:
                break
            
            free_for_this_item = min(remaining_free, item['quantity'])
            if free_for_this_item > 0:
                free_items.append({
                    'product_id': item['product_id'],
                    'quantity': free_for_this_item,
                    'price': item['price']
                })
                remaining_free -= free_for_this_item
        
        discount_amount = sum(
            Decimal(str(item['price'])) * item['quantity'] 
            for item in free_items
        )
        
        return {
            'discount_amount': discount_amount,
            'free_items': free_items,
            'free_shipping': False,
            'description': f'Buy {self.buy_quantity} Get {self.free_quantity} Free'
        }
    
    def _calculate_buy_x_get_discount(self, applicable_items, cart_total):
        """Calculate Buy X Get Discount"""
        total_qty = sum(item['quantity'] for item in applicable_items)
        
        if total_qty < self.buy_quantity:
            return {
                'discount_amount': Decimal('0.00'),
                'free_items': [],
                'free_shipping': False,
                'description': f'Need {self.buy_quantity - total_qty} more items'
            }
        
        if self.discount_type == 'percentage':
            applicable_total = sum(
                Decimal(str(item['price'])) * item['quantity'] 
                for item in applicable_items
            )
            discount_amount = applicable_total * (self.discount_value / 100)
        else:  # fixed_amount
            discount_amount = self.discount_value
        
        return {
            'discount_amount': discount_amount,
            'free_items': [],
            'free_shipping': False,
            'description': f'Buy {self.buy_quantity} Get {self.discount_value}% off'
        }
    
    def _calculate_free_shipping(self, applicable_items):
        """Calculate Free Shipping offer"""
        total_qty = sum(item['quantity'] for item in applicable_items)
        
        if total_qty < self.buy_quantity:
            return {
                'discount_amount': Decimal('0.00'),
                'free_items': [],
                'free_shipping': False,
                'description': f'Need {self.buy_quantity - total_qty} more items for free shipping'
            }
        
        return {
            'discount_amount': Decimal('0.00'),
            'free_items': [],
            'free_shipping': True,
            'description': f'Buy {self.buy_quantity} Get Free Shipping'
        }
    
    def _calculate_bundle_discount(self, applicable_items, cart_total):
        """Calculate Bundle Discount"""
        if len(applicable_items) < self.buy_quantity:
            return {
                'discount_amount': Decimal('0.00'),
                'free_items': [],
                'free_shipping': False,
                'description': f'Need {self.buy_quantity - len(applicable_items)} more different items'
            }
        
        applicable_total = sum(
            Decimal(str(item['price'])) * item['quantity'] 
            for item in applicable_items
        )
        
        if self.discount_type == 'percentage':
            discount_amount = applicable_total * (self.discount_value / 100)
        else:  # fixed_amount
            discount_amount = self.discount_value
        
        return {
            'discount_amount': discount_amount,
            'free_items': [],
            'free_shipping': False,
            'description': f'Bundle discount: {self.discount_value}% off'
        }


class OfferUsage(models.Model):
    """Track offer usage"""
    
    # Polymorphic relationship to both FlashSale and SpecialOffer
    flash_sale = models.ForeignKey(FlashSale, on_delete=models.CASCADE, related_name='usage_records', blank=True, null=True)
    special_offer = models.ForeignKey(SpecialOffer, on_delete=models.CASCADE, related_name='usage_records', blank=True, null=True)
    
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='offer_usage', blank=True, null=True)
    order_id = models.CharField(_('order ID'), max_length=50, blank=True, null=True)
    
    # Usage details
    discount_amount = models.DecimalField(_('discount amount'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    free_shipping_applied = models.BooleanField(_('free shipping applied'), default=False)
    free_items_json = models.JSONField(_('free items'), default=list, blank=True)
    order_total = models.DecimalField(_('order total'), max_digits=10, decimal_places=2)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Offer Usage')
        verbose_name_plural = _('Offer Usages')
        db_table = 'offers_usage'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['order_id']),
            models.Index(fields=['flash_sale']),
            models.Index(fields=['special_offer']),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(flash_sale__isnull=False, special_offer__isnull=True) |
                    models.Q(flash_sale__isnull=True, special_offer__isnull=False)
                ),
                name='offer_usage_exclusive_offer_type'
            ),
        ]
    
    def __str__(self):
        offer_name = ''
        if self.flash_sale:
            offer_name = self.flash_sale.name_en
        elif self.special_offer:
            offer_name = self.special_offer.name_en
        
        user_email = self.user.email if self.user else 'Guest'
        return f"{offer_name} - {user_email} - {self.order_id or 'N/A'}"


class FlashSaleProduct(models.Model):
    """Products included in flash sales with specific discounts"""
    
    flash_sale = models.ForeignKey(FlashSale, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='flash_sale_entries')
    
    # Discount configuration
    discount_type = models.CharField(_('discount type'), max_length=20, choices=[
        ('percentage', _('Percentage')),
        ('fixed_amount', _('Fixed Amount')),
    ], default='percentage')
    discount_value = models.DecimalField(_('discount value'), max_digits=10, decimal_places=2)
    
    # Quantity limits
    quantity_limit = models.PositiveIntegerField(_('quantity limit'), blank=True, null=True, help_text=_('Max quantity available at this price'))
    sold_quantity = models.PositiveIntegerField(_('sold quantity'), default=0)
    
    # Display settings
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    is_featured = models.BooleanField(_('is featured'), default=False)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Flash Sale Product')
        verbose_name_plural = _('Flash Sale Products')
        db_table = 'offers_flash_sale_products'
        unique_together = ['flash_sale', 'product']
        ordering = ['-is_featured', 'display_order', 'product__name_en']
        indexes = [
            models.Index(fields=['flash_sale', 'is_featured']),
            models.Index(fields=['display_order']),
        ]
    
    def __str__(self):
        return f"{self.flash_sale.name_en} - {self.product.name_en}"
    
    @property
    def discounted_price(self):
        """Calculate discounted price"""
        if self.discount_type == 'percentage':
            discount_amount = self.product.price * (self.discount_value / 100)
            return self.product.price - discount_amount
        else:  # fixed_amount
            return max(self.product.price - self.discount_value, Decimal('0.00'))
    
    @property
    def discount_amount(self):
        """Calculate discount amount"""
        return self.product.price - self.discounted_price
    
    @property
    def is_available(self):
        """Check if product is still available in flash sale"""
        if not self.flash_sale.is_running:
            return False
        
        if self.quantity_limit and self.sold_quantity >= self.quantity_limit:
            return False
        
        return True
    
    @property
    def remaining_quantity(self):
        """Get remaining quantity"""
        if not self.quantity_limit:
            return None
        return max(self.quantity_limit - self.sold_quantity, 0)
