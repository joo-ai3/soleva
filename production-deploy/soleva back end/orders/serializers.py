from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import (
    Order, OrderItem, OrderStatusHistory, OrderPayment,
    OrderShipment, OrderRefund, PaymentProof
)
from users.models import Address
from cart.models import Cart

User = get_user_model()


class OrderItemSerializer(serializers.ModelSerializer):
    """Order item serializer"""
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_id', 'product_name', 'product_sku', 'product_image',
            'variant_id', 'variant_sku', 'variant_attributes',
            'unit_price', 'quantity', 'total_price', 'quantity_fulfilled',
            'is_fulfilled', 'pending_quantity'
        ]
        read_only_fields = ['id', 'total_price', 'is_fulfilled', 'pending_quantity']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Order status history serializer"""
    
    changed_by_name = serializers.CharField(source='changed_by.full_name', read_only=True)
    
    class Meta:
        model = OrderStatusHistory
        fields = [
            'id', 'previous_status', 'new_status', 'comment',
            'changed_by', 'changed_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class OrderPaymentSerializer(serializers.ModelSerializer):
    """Order payment serializer"""
    
    class Meta:
        model = OrderPayment
        fields = [
            'id', 'payment_method', 'amount', 'currency',
            'gateway_transaction_id', 'gateway_reference',
            'status', 'created_at', 'processed_at'
        ]
        read_only_fields = ['id', 'created_at', 'processed_at']


class OrderShipmentSerializer(serializers.ModelSerializer):
    """Order shipment serializer"""
    
    class Meta:
        model = OrderShipment
        fields = [
            'id', 'tracking_number', 'courier_company', 'shipping_cost',
            'status', 'tracking_url', 'estimated_delivery',
            'created_at', 'shipped_at', 'delivered_at'
        ]
        read_only_fields = ['id', 'created_at']


class OrderRefundSerializer(serializers.ModelSerializer):
    """Order refund serializer"""
    
    processed_by_name = serializers.CharField(source='processed_by.full_name', read_only=True)
    
    class Meta:
        model = OrderRefund
        fields = [
            'id', 'amount', 'reason', 'status',
            'processed_by', 'processed_by_name', 'gateway_refund_id',
            'created_at', 'processed_at'
        ]
        read_only_fields = ['id', 'created_at', 'processed_at']


class PaymentProofSerializer(serializers.ModelSerializer):
    """Payment proof serializer"""
    
    file_size_mb = serializers.ReadOnlyField()
    is_verified = serializers.ReadOnlyField()
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.full_name', read_only=True)
    
    class Meta:
        model = PaymentProof
        fields = [
            'id', 'image', 'original_filename', 'file_size', 'file_size_mb',
            'verification_status', 'verification_notes', 'verified_at',
            'description', 'created_at', 'updated_at',
            'uploaded_by_name', 'verified_by_name', 'is_verified'
        ]
        read_only_fields = [
            'id', 'file_size', 'uploaded_by_name', 'verified_by_name',
            'verified_at', 'created_at', 'updated_at'
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """Order list serializer (minimal data)"""
    
    items_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'payment_status', 'payment_status_display', 'payment_method',
            'total_amount', 'items_count', 'created_at', 'confirmed_at',
            'shipped_at', 'delivered_at'
        ]
    
    def get_items_count(self, obj):
        """Get total items count"""
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Order detail serializer (complete data)"""
    
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    payments = OrderPaymentSerializer(many=True, read_only=True)
    shipments = OrderShipmentSerializer(many=True, read_only=True)
    refunds = OrderRefundSerializer(many=True, read_only=True)
    payment_proofs = PaymentProofSerializer(many=True, read_only=True)
    
    # Calculated fields
    is_paid = serializers.ReadOnlyField()
    can_be_cancelled = serializers.ReadOnlyField()
    full_shipping_address = serializers.ReadOnlyField()
    
    # Display fields
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    fulfillment_status_display = serializers.CharField(source='get_fulfillment_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'status', 'status_display',
            'payment_status', 'payment_status_display',
            'fulfillment_status', 'fulfillment_status_display',
            
            # Customer information
            'customer_email', 'customer_phone', 'customer_name',
            
            # Addresses
            'shipping_address_line1', 'shipping_address_line2',
            'shipping_city', 'shipping_governorate', 'shipping_postal_code',
            'shipping_phone', 'shipping_name', 'full_shipping_address',
            
            'billing_address_line1', 'billing_address_line2',
            'billing_city', 'billing_governorate', 'billing_postal_code',
            'billing_phone', 'billing_name',
            
            # Order totals
            'subtotal', 'shipping_cost', 'tax_amount', 'discount_amount', 'total_amount',
            
            # Payment & shipping
            'payment_method', 'payment_reference',
            'shipping_method', 'tracking_number', 'courier_company',
            'estimated_delivery_date',
            
            # Coupon
            'coupon_code', 'coupon_discount',
            
            # Notes
            'customer_notes', 'admin_notes', 'language',
            
            # Calculated fields
            'is_paid', 'can_be_cancelled',
            
            # Related data
            'items', 'status_history', 'payments', 'shipments', 'refunds', 'payment_proofs',
            
            # Timestamps
            'created_at', 'updated_at', 'confirmed_at',
            'shipped_at', 'delivered_at', 'cancelled_at'
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Order creation serializer"""
    
    # Shipping address (required)
    shipping_address_id = serializers.IntegerField()
    
    # Billing address (optional, defaults to shipping)
    billing_address_id = serializers.IntegerField(required=False, allow_null=True)
    
    # Payment method
    payment_method = serializers.ChoiceField(
        choices=[
            ('cash_on_delivery', 'Cash on Delivery'),
            ('paymob', 'Paymob'),
            ('stripe', 'Stripe'),
            ('bank_transfer', 'Bank Transfer'),
        ],
        default='cash_on_delivery'
    )
    
    # Optional fields
    customer_notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    def validate_shipping_address_id(self, value):
        """Validate shipping address"""
        user = self.context['request'].user
        try:
            address = Address.objects.get(id=value, user=user, is_active=True)
            return address
        except Address.DoesNotExist:
            raise serializers.ValidationError("Shipping address not found.")
    
    def validate_billing_address_id(self, value):
        """Validate billing address"""
        if value is None:
            return None
        
        user = self.context['request'].user
        try:
            address = Address.objects.get(id=value, user=user, is_active=True)
            return address
        except Address.DoesNotExist:
            raise serializers.ValidationError("Billing address not found.")
    
    def validate_coupon_code(self, value):
        """Validate coupon code"""
        if not value:
            return None
        
        from coupons.models import Coupon
        try:
            coupon = Coupon.objects.get(code=value.upper(), is_active=True)
            user = self.context['request'].user
            
            # Get cart total for validation
            cart = Cart.objects.get(user=user)
            can_use, message = coupon.can_be_used_by_customer(user, cart.subtotal)
            
            if not can_use:
                raise serializers.ValidationError(message)
            
            return coupon
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code.")
    
    def validate(self, attrs):
        """Validate order creation data"""
        user = self.context['request'].user
        
        # Check if user has items in cart
        try:
            cart = Cart.objects.get(user=user)
            if not cart.items.exists():
                raise serializers.ValidationError("Cart is empty.")
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart not found.")
        
        attrs['cart'] = cart
        return attrs


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Order update serializer (admin only)"""
    
    class Meta:
        model = Order
        fields = [
            'status', 'payment_status', 'fulfillment_status',
            'tracking_number', 'courier_company', 'estimated_delivery_date',
            'admin_notes'
        ]
    
    def validate_status(self, value):
        """Validate status transition"""
        if self.instance:
            current_status = self.instance.status
            
            # Define allowed status transitions
            allowed_transitions = {
                'pending': ['confirmed', 'cancelled'],
                'confirmed': ['processing', 'cancelled'],
                'processing': ['shipped', 'cancelled'],
                'shipped': ['out_for_delivery', 'delivered'],
                'out_for_delivery': ['delivered', 'failed_delivery'],
                'delivered': ['returned'],  # Only if return requested
                'cancelled': [],  # Cannot change from cancelled
                'refunded': [],   # Cannot change from refunded
                'returned': [],   # Cannot change from returned
            }
            
            if value not in allowed_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot change status from '{current_status}' to '{value}'"
                )
        
        return value


class OrderTrackingSerializer(serializers.Serializer):
    """Order tracking information serializer"""
    
    order_number = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    tracking_number = serializers.CharField(read_only=True)
    courier_company = serializers.CharField(read_only=True)
    estimated_delivery_date = serializers.DateField(read_only=True)
    
    # Timeline
    timeline = serializers.ListField(read_only=True)
    
    # Current location (if available)
    current_location = serializers.CharField(read_only=True)
    last_update = serializers.DateTimeField(read_only=True)


class OrderStatsSerializer(serializers.Serializer):
    """Order statistics serializer"""
    
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    confirmed_orders = serializers.IntegerField()
    shipped_orders = serializers.IntegerField()
    delivered_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Today's stats
    today_orders = serializers.IntegerField()
    today_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # This month's stats
    month_orders = serializers.IntegerField()
    month_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)


class PaymentProofUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading payment proof"""
    
    class Meta:
        model = PaymentProof
        fields = ['image', 'description']
    
    def validate_image(self, value):
        """Validate uploaded image"""
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Image size cannot exceed 10MB.")
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Only JPEG, PNG, GIF, and WebP images are allowed."
            )
        
        return value
    
    def create(self, validated_data):
        """Create payment proof with additional data"""
        request = self.context.get('request')
        order_id = self.context.get('order_id')
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        payment_proof = PaymentProof.objects.create(
            order_id=order_id,
            uploaded_by=request.user if request.user.is_authenticated else None,
            upload_ip=ip,
            **validated_data
        )
        
        return payment_proof


class PaymentProofVerificationSerializer(serializers.ModelSerializer):
    """Serializer for verifying payment proof (admin only)"""
    
    class Meta:
        model = PaymentProof
        fields = ['verification_status', 'verification_notes']
    
    def validate_verification_status(self, value):
        """Validate verification status"""
        if value not in ['verified', 'rejected', 'needs_clarification']:
            raise serializers.ValidationError("Invalid verification status.")
        return value
    
    def update(self, instance, validated_data):
        """Update verification status with timestamp"""
        from django.utils import timezone
        
        instance.verification_status = validated_data.get('verification_status', instance.verification_status)
        instance.verification_notes = validated_data.get('verification_notes', instance.verification_notes)
        instance.verified_by = self.context['request'].user
        instance.verified_at = timezone.now()
        instance.save()
        
        return instance
