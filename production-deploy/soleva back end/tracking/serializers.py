from rest_framework import serializers
from .models import TrackingPixel, TrackingEvent, ConversionTracking, AbandonedCart


class TrackingPixelSerializer(serializers.ModelSerializer):
    """Tracking pixel serializer"""
    
    class Meta:
        model = TrackingPixel
        fields = [
            'id', 'name', 'pixel_type', 'pixel_id', 'head_code', 'body_code',
            'track_page_views', 'track_ecommerce', 'server_side_tracking',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TrackingEventSerializer(serializers.ModelSerializer):
    """Tracking event serializer"""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = TrackingEvent
        fields = [
            'id', 'event_name', 'event_type', 'user', 'user_email', 'session_id',
            'ip_address', 'user_agent', 'referrer', 'page_url', 'event_data',
            'product_id', 'product_name', 'product_category', 'product_price',
            'quantity', 'value', 'currency', 'order_id', 'pixel',
            'is_processed', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TrackEventSerializer(serializers.Serializer):
    """Track event request serializer"""
    
    event_name = serializers.CharField(max_length=100)
    event_type = serializers.ChoiceField(
        choices=[
            ('page_view', 'Page View'),
            ('view_content', 'View Content'),
            ('add_to_cart', 'Add to Cart'),
            ('initiate_checkout', 'Initiate Checkout'),
            ('add_payment_info', 'Add Payment Info'),
            ('purchase', 'Purchase'),
            ('search', 'Search'),
            ('lead', 'Lead'),
            ('complete_registration', 'Complete Registration'),
            ('custom', 'Custom Event'),
        ]
    )
    
    # Optional fields
    session_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    page_url = serializers.URLField(required=False, allow_blank=True)
    referrer = serializers.URLField(required=False, allow_blank=True)
    
    # E-commerce data
    product_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    product_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    product_category = serializers.CharField(max_length=255, required=False, allow_blank=True)
    product_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    quantity = serializers.IntegerField(required=False, allow_null=True)
    value = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    currency = serializers.CharField(max_length=3, default='EGP')
    order_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    # Additional event data
    event_data = serializers.JSONField(required=False, default=dict)
    
    # Pixel selection
    pixel_types = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
        help_text="List of pixel types to track this event (e.g., ['facebook', 'google_analytics'])"
    )


class ConversionTrackingSerializer(serializers.ModelSerializer):
    """Conversion tracking serializer"""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    conversion_rate = serializers.ReadOnlyField()
    time_to_purchase = serializers.ReadOnlyField()
    
    class Meta:
        model = ConversionTracking
        fields = [
            'id', 'user', 'user_email', 'session_id',
            'landing_at', 'product_view_at', 'add_to_cart_at',
            'checkout_start_at', 'payment_info_at', 'purchase_at',
            'first_product_viewed', 'products_viewed', 'cart_value',
            'order_value', 'order_id', 'utm_source', 'utm_medium',
            'utm_campaign', 'utm_term', 'utm_content', 'referrer',
            'device_type', 'browser', 'operating_system',
            'country', 'city', 'conversion_rate', 'time_to_purchase',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AbandonedCartSerializer(serializers.ModelSerializer):
    """Abandoned cart serializer"""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = AbandonedCart
        fields = [
            'id', 'user', 'user_email', 'session_id', 'cart_items',
            'cart_value', 'recovery_emails_sent', 'last_recovery_email_sent',
            'is_recovered', 'recovered_at', 'recovery_order_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PixelConfigSerializer(serializers.Serializer):
    """Pixel configuration for frontend"""
    
    facebook_pixel_id = serializers.CharField(required=False, allow_blank=True)
    google_analytics_id = serializers.CharField(required=False, allow_blank=True)
    google_gtm_id = serializers.CharField(required=False, allow_blank=True)
    tiktok_pixel_id = serializers.CharField(required=False, allow_blank=True)
    snapchat_pixel_id = serializers.CharField(required=False, allow_blank=True)
    
    # Custom pixels
    custom_pixels = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )


class ConversionFunnelSerializer(serializers.Serializer):
    """Conversion funnel analytics serializer"""
    
    total_sessions = serializers.IntegerField()
    landing_page = serializers.IntegerField()
    product_views = serializers.IntegerField()
    add_to_cart = serializers.IntegerField()
    checkout_start = serializers.IntegerField()
    payment_info = serializers.IntegerField()
    purchases = serializers.IntegerField()
    
    # Conversion rates
    landing_to_product_rate = serializers.FloatField()
    product_to_cart_rate = serializers.FloatField()
    cart_to_checkout_rate = serializers.FloatField()
    checkout_to_payment_rate = serializers.FloatField()
    payment_to_purchase_rate = serializers.FloatField()
    overall_conversion_rate = serializers.FloatField()


class TrackingStatsSerializer(serializers.Serializer):
    """Tracking statistics serializer"""
    
    # Event counts
    total_events = serializers.IntegerField()
    page_views = serializers.IntegerField()
    product_views = serializers.IntegerField()
    add_to_cart_events = serializers.IntegerField()
    purchase_events = serializers.IntegerField()
    
    # Conversion data
    total_conversions = serializers.IntegerField()
    conversion_rate = serializers.FloatField()
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Abandoned carts
    abandoned_carts = serializers.IntegerField()
    recovered_carts = serializers.IntegerField()
    cart_recovery_rate = serializers.FloatField()
    
    # Time periods
    today_events = serializers.IntegerField()
    week_events = serializers.IntegerField()
    month_events = serializers.IntegerField()
    
    # Top sources
    top_traffic_sources = serializers.ListField(child=serializers.DictField())
    top_products = serializers.ListField(child=serializers.DictField())


class UTMParametersSerializer(serializers.Serializer):
    """UTM parameters serializer"""
    
    utm_source = serializers.CharField(max_length=255, required=False, allow_blank=True)
    utm_medium = serializers.CharField(max_length=255, required=False, allow_blank=True)
    utm_campaign = serializers.CharField(max_length=255, required=False, allow_blank=True)
    utm_term = serializers.CharField(max_length=255, required=False, allow_blank=True)
    utm_content = serializers.CharField(max_length=255, required=False, allow_blank=True)
    
    # Additional tracking parameters
    gclid = serializers.CharField(max_length=255, required=False, allow_blank=True)  # Google Ads
    fbclid = serializers.CharField(max_length=255, required=False, allow_blank=True)  # Facebook Ads
    ttclid = serializers.CharField(max_length=255, required=False, allow_blank=True)  # TikTok Ads
