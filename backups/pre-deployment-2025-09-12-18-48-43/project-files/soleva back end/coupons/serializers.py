from rest_framework import serializers
from decimal import Decimal
from django.utils import timezone
from .models import Coupon, CouponUsage


class CouponSerializer(serializers.ModelSerializer):
    """Coupon serializer for listing and details"""
    
    usage_count = serializers.IntegerField(read_only=True)
    is_expired = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'name_en', 'name_ar', 'description_en', 'description_ar',
            'discount_type', 'discount_value', 'max_discount_amount',
            'minimum_order_amount', 'usage_limit', 'usage_limit_per_customer',
            'free_shipping', 'valid_from', 'valid_until', 'is_active',
            'created_at', 'updated_at', 'usage_count', 'is_expired', 'days_until_expiry'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_is_expired(self, obj):
        """Check if coupon is expired"""
        if obj.valid_until:
            return obj.valid_until < timezone.now().date()
        return False
    
    def get_days_until_expiry(self, obj):
        """Get days until coupon expires"""
        if obj.valid_until:
            days = (obj.valid_until - timezone.now().date()).days
            return max(days, 0)
        return None


class CouponCreateUpdateSerializer(serializers.ModelSerializer):
    """Coupon serializer for create and update operations"""
    
    class Meta:
        model = Coupon
        fields = [
            'code', 'name_en', 'name_ar', 'description_en', 'description_ar',
            'discount_type', 'discount_value', 'max_discount_amount',
            'minimum_order_amount', 'usage_limit', 'usage_limit_per_customer',
            'free_shipping', 'valid_from', 'valid_until', 'is_active'
        ]
    
    def validate_code(self, value):
        """Validate coupon code"""
        value = value.upper().strip()
        
        if len(value) < 3:
            raise serializers.ValidationError("Coupon code must be at least 3 characters long.")
        
        if len(value) > 20:
            raise serializers.ValidationError("Coupon code cannot be longer than 20 characters.")
        
        # Check uniqueness (excluding current instance for updates)
        queryset = Coupon.objects.filter(code=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("A coupon with this code already exists.")
        
        return value
    
    def validate_discount_value(self, value):
        """Validate discount value"""
        if value <= 0:
            raise serializers.ValidationError("Discount value must be greater than 0.")
        
        # If discount type is percentage, ensure it's not more than 100%
        discount_type = self.initial_data.get('discount_type')
        if discount_type == 'percentage' and value > 100:
            raise serializers.ValidationError("Percentage discount cannot be more than 100%.")
        
        return value
    
    def validate_minimum_order_amount(self, value):
        """Validate minimum order amount"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Minimum order amount cannot be negative.")
        return value
    
    def validate_max_discount_amount(self, value):
        """Validate maximum discount amount"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Maximum discount amount must be greater than 0.")
        return value
    
    def validate_usage_limit(self, value):
        """Validate usage limit"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Usage limit must be greater than 0.")
        return value
    
    def validate_usage_limit_per_customer(self, value):
        """Validate usage limit per customer"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Usage limit per customer must be greater than 0.")
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        valid_from = attrs.get('valid_from')
        valid_until = attrs.get('valid_until')
        
        if valid_from and valid_until and valid_from >= valid_until:
            raise serializers.ValidationError({
                'valid_until': 'Valid until date must be after valid from date.'
            })
        
        # Ensure percentage discounts have max_discount_amount for large orders
        discount_type = attrs.get('discount_type')
        discount_value = attrs.get('discount_value')
        max_discount_amount = attrs.get('max_discount_amount')
        
        if (discount_type == 'percentage' and 
            discount_value and discount_value > 50 and 
            not max_discount_amount):
            raise serializers.ValidationError({
                'max_discount_amount': 'Maximum discount amount is recommended for percentage discounts over 50%.'
            })
        
        return attrs


class CouponUsageSerializer(serializers.ModelSerializer):
    """Coupon usage serializer"""
    
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    coupon_name = serializers.CharField(source='coupon.name_en', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = CouponUsage
        fields = [
            'id', 'coupon_code', 'coupon_name', 'user_email', 'user_full_name',
            'order_id', 'order_total', 'discount_amount', 'created_at'
        ]
        read_only_fields = ['created_at']


class CouponValidationSerializer(serializers.Serializer):
    """Serializer for coupon validation requests"""
    
    code = serializers.CharField(max_length=20)
    cart_total = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        default=Decimal('0.00')
    )
    
    def validate_code(self, value):
        """Validate and clean coupon code"""
        return value.upper().strip()
    
    def validate_cart_total(self, value):
        """Validate cart total"""
        if value < 0:
            raise serializers.ValidationError("Cart total cannot be negative.")
        return value


class CouponApplicationSerializer(serializers.Serializer):
    """Serializer for applying coupons"""
    
    code = serializers.CharField(max_length=20)
    cart_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_code(self, value):
        """Validate and clean coupon code"""
        return value.upper().strip()
    
    def validate_cart_total(self, value):
        """Validate cart total"""
        if value <= 0:
            raise serializers.ValidationError("Cart total must be greater than 0.")
        return value


class CouponSummarySerializer(serializers.Serializer):
    """Serializer for coupon summary in checkout"""
    
    id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    discount_type = serializers.CharField()
    discount_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    free_shipping = serializers.BooleanField()
    
    class Meta:
        fields = [
            'id', 'code', 'name', 'description', 'discount_type',
            'discount_value', 'discount_amount', 'free_shipping'
        ]
