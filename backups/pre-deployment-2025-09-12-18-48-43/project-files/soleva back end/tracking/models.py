from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class TrackingPixel(models.Model):
    """Configuration for tracking pixels"""
    
    # Pixel identification
    name = models.CharField(_('name'), max_length=100, unique=True)
    pixel_type = models.CharField(
        _('pixel type'),
        max_length=50,
        choices=[
            ('facebook', _('Facebook Pixel')),
            ('google_analytics', _('Google Analytics')),
            ('google_gtm', _('Google Tag Manager')),
            ('tiktok', _('TikTok Pixel')),
            ('snapchat', _('Snapchat Pixel')),
            ('twitter', _('Twitter Pixel')),
            ('pinterest', _('Pinterest Tag')),
            ('linkedin', _('LinkedIn Insight Tag')),
            ('custom', _('Custom Pixel')),
        ]
    )
    
    # Pixel configuration
    pixel_id = models.CharField(_('pixel ID'), max_length=255)
    access_token = models.CharField(_('access token'), max_length=500, blank=True)
    
    # Custom pixel code
    head_code = models.TextField(_('head code'), blank=True, help_text=_('Code to be placed in <head>'))
    body_code = models.TextField(_('body code'), blank=True, help_text=_('Code to be placed in <body>'))
    
    # Configuration
    track_page_views = models.BooleanField(_('track page views'), default=True)
    track_ecommerce = models.BooleanField(_('track e-commerce events'), default=True)
    server_side_tracking = models.BooleanField(_('server-side tracking'), default=False)
    
    # Status
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Tracking Pixel')
        verbose_name_plural = _('Tracking Pixels')
        db_table = 'tracking_pixels'
        indexes = [
            models.Index(fields=['pixel_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.pixel_type})"


class TrackingEvent(models.Model):
    """Log tracking events"""
    
    # Event identification
    event_name = models.CharField(_('event name'), max_length=100)
    event_type = models.CharField(
        _('event type'),
        max_length=50,
        choices=[
            ('page_view', _('Page View')),
            ('view_content', _('View Content')),
            ('add_to_cart', _('Add to Cart')),
            ('initiate_checkout', _('Initiate Checkout')),
            ('add_payment_info', _('Add Payment Info')),
            ('purchase', _('Purchase')),
            ('search', _('Search')),
            ('lead', _('Lead')),
            ('complete_registration', _('Complete Registration')),
            ('custom', _('Custom Event')),
        ]
    )
    
    # User information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(_('session ID'), max_length=100, blank=True)
    
    # Request information
    ip_address = models.GenericIPAddressField(_('IP address'), blank=True, null=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    referrer = models.URLField(_('referrer'), blank=True)
    page_url = models.URLField(_('page URL'), blank=True)
    
    # Event data
    event_data = models.JSONField(_('event data'), default=dict, blank=True)
    
    # E-commerce specific data
    product_id = models.CharField(_('product ID'), max_length=100, blank=True)
    product_name = models.CharField(_('product name'), max_length=255, blank=True)
    product_category = models.CharField(_('product category'), max_length=255, blank=True)
    product_price = models.DecimalField(_('product price'), max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.PositiveIntegerField(_('quantity'), blank=True, null=True)
    value = models.DecimalField(_('value'), max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(_('currency'), max_length=3, default='EGP')
    
    # Order information (for purchase events)
    order_id = models.CharField(_('order ID'), max_length=100, blank=True)
    
    # Pixel information
    pixel = models.ForeignKey(TrackingPixel, on_delete=models.CASCADE, related_name='events')
    
    # Processing status
    is_processed = models.BooleanField(_('is processed'), default=False)
    processed_at = models.DateTimeField(_('processed at'), blank=True, null=True)
    error_message = models.TextField(_('error message'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Tracking Event')
        verbose_name_plural = _('Tracking Events')
        db_table = 'tracking_events'
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['session_id']),
            models.Index(fields=['pixel', 'is_processed']),
            models.Index(fields=['order_id']),
        ]
    
    def __str__(self):
        return f"{self.event_name} - {self.pixel.name}"


class ConversionTracking(models.Model):
    """Track conversion funnels"""
    
    # User identification
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(_('session ID'), max_length=100)
    
    # Funnel steps
    FUNNEL_STEPS = [
        ('landing', _('Landing Page')),
        ('product_view', _('Product View')),
        ('add_to_cart', _('Add to Cart')),
        ('checkout_start', _('Checkout Start')),
        ('payment_info', _('Payment Info')),
        ('purchase', _('Purchase')),
    ]
    
    # Track each step
    landing_at = models.DateTimeField(_('landing at'), blank=True, null=True)
    product_view_at = models.DateTimeField(_('product view at'), blank=True, null=True)
    add_to_cart_at = models.DateTimeField(_('add to cart at'), blank=True, null=True)
    checkout_start_at = models.DateTimeField(_('checkout start at'), blank=True, null=True)
    payment_info_at = models.DateTimeField(_('payment info at'), blank=True, null=True)
    purchase_at = models.DateTimeField(_('purchase at'), blank=True, null=True)
    
    # Conversion details
    first_product_viewed = models.CharField(_('first product viewed'), max_length=255, blank=True)
    products_viewed = models.JSONField(_('products viewed'), default=list, blank=True)
    cart_value = models.DecimalField(_('cart value'), max_digits=10, decimal_places=2, blank=True, null=True)
    order_value = models.DecimalField(_('order value'), max_digits=10, decimal_places=2, blank=True, null=True)
    order_id = models.CharField(_('order ID'), max_length=100, blank=True)
    
    # Attribution
    utm_source = models.CharField(_('UTM source'), max_length=255, blank=True)
    utm_medium = models.CharField(_('UTM medium'), max_length=255, blank=True)
    utm_campaign = models.CharField(_('UTM campaign'), max_length=255, blank=True)
    utm_term = models.CharField(_('UTM term'), max_length=255, blank=True)
    utm_content = models.CharField(_('UTM content'), max_length=255, blank=True)
    referrer = models.URLField(_('referrer'), blank=True)
    
    # Device information
    device_type = models.CharField(_('device type'), max_length=50, blank=True)
    browser = models.CharField(_('browser'), max_length=100, blank=True)
    operating_system = models.CharField(_('operating system'), max_length=100, blank=True)
    
    # Geographic information
    country = models.CharField(_('country'), max_length=100, blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Conversion Tracking')
        verbose_name_plural = _('Conversion Tracking')
        db_table = 'conversion_tracking'
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['utm_source', 'utm_campaign']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Conversion {self.session_id}"
    
    @property
    def conversion_rate(self):
        """Calculate conversion rate for this session"""
        steps_completed = sum([
            1 if self.landing_at else 0,
            1 if self.product_view_at else 0,
            1 if self.add_to_cart_at else 0,
            1 if self.checkout_start_at else 0,
            1 if self.payment_info_at else 0,
            1 if self.purchase_at else 0,
        ])
        return (steps_completed / 6) * 100
    
    @property
    def time_to_purchase(self):
        """Calculate time from landing to purchase"""
        if self.landing_at and self.purchase_at:
            return self.purchase_at - self.landing_at
        return None


class AbandonedCart(models.Model):
    """Track abandoned carts for recovery"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='abandoned_carts')
    session_id = models.CharField(_('session ID'), max_length=100)
    
    # Cart details
    cart_items = models.JSONField(_('cart items'), default=list)
    cart_value = models.DecimalField(_('cart value'), max_digits=10, decimal_places=2)
    
    # Recovery attempts
    recovery_emails_sent = models.PositiveIntegerField(_('recovery emails sent'), default=0)
    last_recovery_email_sent = models.DateTimeField(_('last recovery email sent'), blank=True, null=True)
    
    # Status
    is_recovered = models.BooleanField(_('is recovered'), default=False)
    recovered_at = models.DateTimeField(_('recovered at'), blank=True, null=True)
    recovery_order_id = models.CharField(_('recovery order ID'), max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Abandoned Cart')
        verbose_name_plural = _('Abandoned Carts')
        db_table = 'abandoned_carts'
        indexes = [
            models.Index(fields=['user', 'is_recovered']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Abandoned cart - {self.user.email} - {self.cart_value}"
