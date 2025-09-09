from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class Governorate(models.Model):
    """Egypt governorates"""
    
    name_en = models.CharField(_('name (English)'), max_length=100, unique=True)
    name_ar = models.CharField(_('name (Arabic)'), max_length=100, unique=True)
    code = models.CharField(_('code'), max_length=10, unique=True)
    
    # Geographic info
    latitude = models.DecimalField(_('latitude'), max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(_('longitude'), max_digits=11, decimal_places=8, blank=True, null=True)
    
    # Shipping settings
    is_active = models.BooleanField(_('is active'), default=True)
    base_shipping_cost = models.DecimalField(_('base shipping cost'), max_digits=8, decimal_places=2, default=Decimal('30.00'))
    
    # Display settings
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    
    class Meta:
        verbose_name = _('Governorate')
        verbose_name_plural = _('Governorates')
        db_table = 'shipping_governorates'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'display_order']),
        ]
    
    def __str__(self):
        return self.name_en


class City(models.Model):
    """Cities/Markaz within governorates"""
    
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE, related_name='cities')
    name_en = models.CharField(_('name (English)'), max_length=100)
    name_ar = models.CharField(_('name (Arabic)'), max_length=100)
    
    # Geographic info
    latitude = models.DecimalField(_('latitude'), max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(_('longitude'), max_digits=11, decimal_places=8, blank=True, null=True)
    
    # Shipping settings
    is_active = models.BooleanField(_('is active'), default=True)
    additional_shipping_cost = models.DecimalField(_('additional shipping cost'), max_digits=8, decimal_places=2, default=Decimal('0.00'))
    estimated_delivery_days = models.PositiveIntegerField(_('estimated delivery days'), default=3)
    
    # Display settings
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    
    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')
        db_table = 'shipping_cities'
        constraints = [
            models.UniqueConstraint(
                fields=['governorate', 'name_en'],
                name='unique_city_per_governorate'
            ),
        ]
        indexes = [
            models.Index(fields=['governorate', 'is_active']),
            models.Index(fields=['name_en']),
            models.Index(fields=['name_ar']),
        ]
    
    def __str__(self):
        return f"{self.name_en}, {self.governorate.name_en}"
    
    @property
    def total_shipping_cost(self):
        """Get total shipping cost (governorate base + city additional)"""
        return self.governorate.base_shipping_cost + self.additional_shipping_cost


class ShippingMethod(models.Model):
    """Available shipping methods"""
    
    name_en = models.CharField(_('name (English)'), max_length=100)
    name_ar = models.CharField(_('name (Arabic)'), max_length=100)
    code = models.CharField(_('code'), max_length=50, unique=True)
    description_en = models.TextField(_('description (English)'), blank=True)
    description_ar = models.TextField(_('description (Arabic)'), blank=True)
    
    # Pricing
    base_cost = models.DecimalField(_('base cost'), max_digits=8, decimal_places=2)
    cost_per_kg = models.DecimalField(_('cost per kg'), max_digits=8, decimal_places=2, default=Decimal('0.00'))
    free_shipping_threshold = models.DecimalField(_('free shipping threshold'), max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Delivery settings
    min_delivery_days = models.PositiveIntegerField(_('minimum delivery days'), default=1)
    max_delivery_days = models.PositiveIntegerField(_('maximum delivery days'), default=7)
    
    # Restrictions
    max_weight = models.DecimalField(_('maximum weight (kg)'), max_digits=8, decimal_places=3, blank=True, null=True)
    max_dimensions = models.CharField(_('maximum dimensions (LxWxH cm)'), max_length=50, blank=True)
    
    # Status
    is_active = models.BooleanField(_('is active'), default=True)
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Shipping Method')
        verbose_name_plural = _('Shipping Methods')
        db_table = 'shipping_methods'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'display_order']),
        ]
    
    def __str__(self):
        return self.name_en
    
    def calculate_cost(self, total_weight=0, order_total=0):
        """Calculate shipping cost based on weight and order total"""
        # Check if eligible for free shipping
        if self.free_shipping_threshold and order_total >= self.free_shipping_threshold:
            return Decimal('0.00')
        
        # Calculate cost
        cost = self.base_cost
        if total_weight > 0:
            cost += self.cost_per_kg * Decimal(str(total_weight))
        
        return cost


class ShippingZone(models.Model):
    """Shipping zones for different pricing"""
    
    name_en = models.CharField(_('name (English)'), max_length=100)
    name_ar = models.CharField(_('name (Arabic)'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    
    # Zone settings
    governorates = models.ManyToManyField(Governorate, related_name='shipping_zones')
    
    # Status
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Shipping Zone')
        verbose_name_plural = _('Shipping Zones')
        db_table = 'shipping_zones'
    
    def __str__(self):
        return self.name_en


class ShippingRate(models.Model):
    """Shipping rates for zones and methods"""
    
    zone = models.ForeignKey(ShippingZone, on_delete=models.CASCADE, related_name='rates')
    method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE, related_name='zone_rates')
    
    # Pricing
    base_cost = models.DecimalField(_('base cost'), max_digits=8, decimal_places=2)
    cost_per_kg = models.DecimalField(_('cost per kg'), max_digits=8, decimal_places=2, default=Decimal('0.00'))
    
    # Weight ranges
    min_weight = models.DecimalField(_('minimum weight (kg)'), max_digits=8, decimal_places=3, default=Decimal('0.000'))
    max_weight = models.DecimalField(_('maximum weight (kg)'), max_digits=8, decimal_places=3, blank=True, null=True)
    
    # Order value ranges
    min_order_value = models.DecimalField(_('minimum order value'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    max_order_value = models.DecimalField(_('maximum order value'), max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Shipping Rate')
        verbose_name_plural = _('Shipping Rates')
        db_table = 'shipping_rates'
        constraints = [
            models.UniqueConstraint(
                fields=['zone', 'method', 'min_weight', 'min_order_value'],
                name='unique_shipping_rate'
            ),
        ]
        indexes = [
            models.Index(fields=['zone', 'method']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.zone.name_en} - {self.method.name_en}"
    
    def calculate_cost(self, weight, order_value):
        """Calculate shipping cost for given weight and order value"""
        if not self.is_applicable(weight, order_value):
            return None
        
        cost = self.base_cost
        if weight > 0:
            cost += self.cost_per_kg * Decimal(str(weight))
        
        return cost
    
    def is_applicable(self, weight, order_value):
        """Check if this rate is applicable for given weight and order value"""
        # Check weight range
        if weight < self.min_weight:
            return False
        if self.max_weight and weight > self.max_weight:
            return False
        
        # Check order value range
        if order_value < self.min_order_value:
            return False
        if self.max_order_value and order_value > self.max_order_value:
            return False
        
        return True
