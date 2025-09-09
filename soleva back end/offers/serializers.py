from rest_framework import serializers
from django.utils import timezone
from .models import FlashSale, SpecialOffer, OfferUsage, FlashSaleProduct


class FlashSaleProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name_en', read_only=True)
    product_name_ar = serializers.CharField(source='product.name_ar', read_only=True)
    product_image = serializers.ImageField(source='product.image_url', read_only=True)
    original_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining_quantity = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = FlashSaleProduct
        fields = [
            'id', 'product', 'product_name', 'product_name_ar', 'product_image',
            'discount_type', 'discount_value', 'original_price', 'discounted_price',
            'discount_amount', 'quantity_limit', 'sold_quantity', 'remaining_quantity',
            'is_featured', 'display_order', 'is_available'
        ]


class FlashSaleSerializer(serializers.ModelSerializer):
    products = FlashSaleProductSerializer(many=True, read_only=True)
    is_running = serializers.BooleanField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    time_remaining = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = FlashSale
        fields = [
            'id', 'name_en', 'name_ar', 'description_en', 'description_ar',
            'start_time', 'end_time', 'banner_image', 'banner_color', 'text_color',
            'display_priority', 'is_active', 'show_countdown', 'max_uses_per_customer',
            'total_usage_limit', 'current_usage_count', 'is_running', 'is_upcoming',
            'is_expired', 'time_remaining', 'products'
        ]


class FlashSaleListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing flash sales"""
    is_running = serializers.BooleanField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    time_remaining = serializers.IntegerField(read_only=True)
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FlashSale
        fields = [
            'id', 'name_en', 'name_ar', 'description_en', 'description_ar',
            'start_time', 'end_time', 'banner_image', 'banner_color', 'text_color',
            'display_priority', 'show_countdown', 'is_running', 'is_upcoming',
            'is_expired', 'time_remaining', 'products_count'
        ]
    
    def get_products_count(self, obj):
        return obj.products.count()


class SpecialOfferSerializer(serializers.ModelSerializer):
    applicable_products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    applicable_categories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    is_running = serializers.BooleanField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    time_remaining = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = SpecialOffer
        fields = [
            'id', 'name_en', 'name_ar', 'description_en', 'description_ar',
            'offer_type', 'buy_quantity', 'free_quantity', 'discount_type',
            'discount_value', 'applicable_products', 'applicable_categories',
            'start_time', 'end_time', 'max_uses_per_customer', 'total_usage_limit',
            'current_usage_count', 'minimum_order_amount', 'button_text_en',
            'button_text_ar', 'button_color', 'highlight_color', 'is_active',
            'show_on_product_page', 'show_timer', 'is_running', 'is_upcoming',
            'is_expired', 'time_remaining'
        ]


class SpecialOfferListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing special offers"""
    is_running = serializers.BooleanField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    time_remaining = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = SpecialOffer
        fields = [
            'id', 'name_en', 'name_ar', 'offer_type', 'buy_quantity',
            'free_quantity', 'discount_type', 'discount_value', 'start_time',
            'end_time', 'button_text_en', 'button_text_ar', 'button_color',
            'highlight_color', 'show_on_product_page', 'show_timer',
            'is_running', 'is_upcoming', 'is_expired', 'time_remaining'
        ]


class OfferCalculationRequestSerializer(serializers.Serializer):
    """Serializer for offer calculation requests"""
    cart_items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    user_id = serializers.UUIDField(required=False, allow_null=True)
    
    def validate_cart_items(self, value):
        """Validate cart items structure"""
        required_fields = ['product_id', 'quantity', 'price']
        
        for item in value:
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(f"Missing field '{field}' in cart item")
        
        return value


class OfferCalculationResponseSerializer(serializers.Serializer):
    """Serializer for offer calculation responses"""
    flash_sales = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )
    special_offers = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )
    best_offer = serializers.DictField(read_only=True, allow_null=True)
    total_discount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    free_shipping_available = serializers.BooleanField(read_only=True)
    coupons_blocked = serializers.BooleanField(read_only=True)


class OfferUsageSerializer(serializers.ModelSerializer):
    flash_sale_name = serializers.CharField(source='flash_sale.name_en', read_only=True)
    special_offer_name = serializers.CharField(source='special_offer.name_en', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = OfferUsage
        fields = [
            'id', 'flash_sale', 'special_offer', 'flash_sale_name',
            'special_offer_name', 'user', 'user_email', 'order_id',
            'discount_amount', 'free_shipping_applied', 'free_items_json',
            'order_total', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class FlashSaleActivationSerializer(serializers.Serializer):
    """Serializer for activating/deactivating flash sales"""
    is_active = serializers.BooleanField()


class SpecialOfferActivationSerializer(serializers.Serializer):
    """Serializer for activating/deactivating special offers"""
    is_active = serializers.BooleanField()


class ProductOfferCheckSerializer(serializers.Serializer):
    """Serializer for checking offers available for a specific product"""
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(default=1, min_value=1)
    user_id = serializers.UUIDField(required=False, allow_null=True)


class ProductOfferResponseSerializer(serializers.Serializer):
    """Response serializer for product offer checks"""
    flash_sale = FlashSaleProductSerializer(read_only=True, allow_null=True)
    special_offers = SpecialOfferListSerializer(many=True, read_only=True)
    best_discount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, allow_null=True)
    has_active_offers = serializers.BooleanField(read_only=True)
