from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Cart, CartItem, SavedForLater
from products.models import Product, ProductVariant
from products.serializers import ProductListSerializer

User = get_user_model()


class CartItemSerializer(serializers.ModelSerializer):
    """Cart item serializer"""
    
    product_details = serializers.SerializerMethodField()
    variant_details = serializers.SerializerMethodField()
    total_price = serializers.ReadOnlyField()
    is_available = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product_id', 'variant_id', 'quantity',
            'product_name', 'product_price', 'product_image',
            'variant_attributes', 'total_price', 'is_available',
            'product_details', 'variant_details', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'product_name', 'product_price', 'product_image',
            'variant_attributes', 'created_at', 'updated_at'
        ]
    
    def get_product_details(self, obj):
        """Get current product details"""
        try:
            product = Product.objects.get(id=obj.product_id, is_active=True)
            return {
                'id': product.id,
                'name_en': product.name_en,
                'name_ar': product.name_ar,
                'slug': product.slug,
                'price': product.price,
                'compare_price': product.compare_price,
                'is_in_stock': product.is_in_stock,
                'inventory_quantity': product.inventory_quantity if product.track_inventory else None,
            }
        except Product.DoesNotExist:
            return None
    
    def get_variant_details(self, obj):
        """Get current variant details if applicable"""
        if obj.variant_id:
            try:
                variant = ProductVariant.objects.get(
                    id=obj.variant_id, 
                    is_active=True,
                    product__is_active=True
                )
                return {
                    'id': variant.id,
                    'sku': variant.sku,
                    'price': variant.effective_price,
                    'is_in_stock': variant.is_in_stock,
                    'inventory_quantity': variant.inventory_quantity,
                }
            except ProductVariant.DoesNotExist:
                return None
        return None
    
    def get_is_available(self, obj):
        """Check if item is still available"""
        try:
            if obj.variant_id:
                variant = ProductVariant.objects.get(
                    id=obj.variant_id, 
                    is_active=True,
                    product__is_active=True
                )
                return variant.is_in_stock and variant.inventory_quantity >= obj.quantity
            else:
                product = Product.objects.get(id=obj.product_id, is_active=True)
                if not product.track_inventory:
                    return True
                return product.is_in_stock and product.inventory_quantity >= obj.quantity
        except (Product.DoesNotExist, ProductVariant.DoesNotExist):
            return False
    
    def validate_quantity(self, value):
        """Validate quantity"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        if value > 100:  # Max quantity per item
            raise serializers.ValidationError("Maximum quantity per item is 100.")
        return value
    
    def validate(self, attrs):
        """Validate cart item"""
        product_id = attrs.get('product_id')
        variant_id = attrs.get('variant_id')
        quantity = attrs.get('quantity', 1)
        
        # Check if product exists and is active
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive.")
        
        # Check variant if provided
        if variant_id:
            try:
                variant = ProductVariant.objects.get(
                    id=variant_id, 
                    product=product, 
                    is_active=True
                )
                # Check variant stock
                if variant.inventory_quantity < quantity:
                    raise serializers.ValidationError(
                        f"Only {variant.inventory_quantity} items available for this variant."
                    )
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError("Product variant not found or inactive.")
        else:
            # Check product stock
            if product.track_inventory and product.inventory_quantity < quantity:
                raise serializers.ValidationError(
                    f"Only {product.inventory_quantity} items available."
                )
        
        return attrs


class AddToCartSerializer(serializers.Serializer):
    """Add to cart serializer"""
    
    product_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(default=1, min_value=1, max_value=100)
    
    def validate_product_id(self, value):
        """Validate product exists and is active"""
        try:
            Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive.")
        return value
    
    def validate(self, attrs):
        """Validate add to cart data"""
        product_id = attrs['product_id']
        variant_id = attrs.get('variant_id')
        quantity = attrs['quantity']
        
        product = Product.objects.get(id=product_id, is_active=True)
        
        # If variant_id provided, validate it
        if variant_id:
            try:
                variant = ProductVariant.objects.get(
                    id=variant_id, 
                    product=product, 
                    is_active=True
                )
                # Check stock availability
                if variant.inventory_quantity < quantity:
                    raise serializers.ValidationError(
                        f"Only {variant.inventory_quantity} items available for this variant."
                    )
                attrs['variant'] = variant
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError("Product variant not found.")
        else:
            # Check product stock if no variant
            if product.track_inventory and product.inventory_quantity < quantity:
                raise serializers.ValidationError(
                    f"Only {product.inventory_quantity} items available."
                )
        
        attrs['product'] = product
        return attrs


class CartSerializer(serializers.ModelSerializer):
    """Cart serializer"""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()
    items_count = serializers.SerializerMethodField()
    has_unavailable_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'items', 'total_items', 'subtotal', 'items_count',
            'has_unavailable_items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        """Get total number of unique items"""
        return obj.items.count()
    
    def get_has_unavailable_items(self, obj):
        """Check if cart has any unavailable items"""
        for item in obj.items.all():
            serializer = CartItemSerializer(item)
            if not serializer.get_is_available(item):
                return True
        return False


class SavedForLaterSerializer(serializers.ModelSerializer):
    """Saved for later serializer"""
    
    product_details = serializers.SerializerMethodField()
    variant_details = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    
    class Meta:
        model = SavedForLater
        fields = [
            'id', 'product_id', 'variant_id', 'product_name', 
            'product_price', 'product_image', 'variant_attributes',
            'product_details', 'variant_details', 'is_available', 'created_at'
        ]
        read_only_fields = [
            'id', 'product_name', 'product_price', 'product_image',
            'variant_attributes', 'created_at'
        ]
    
    def get_product_details(self, obj):
        """Get current product details"""
        try:
            product = Product.objects.get(id=obj.product_id, is_active=True)
            return ProductListSerializer(product, context=self.context).data
        except Product.DoesNotExist:
            return None
    
    def get_variant_details(self, obj):
        """Get current variant details if applicable"""
        if obj.variant_id:
            try:
                variant = ProductVariant.objects.get(
                    id=obj.variant_id, 
                    is_active=True,
                    product__is_active=True
                )
                return {
                    'id': variant.id,
                    'sku': variant.sku,
                    'price': variant.effective_price,
                    'is_in_stock': variant.is_in_stock,
                }
            except ProductVariant.DoesNotExist:
                return None
        return None
    
    def get_is_available(self, obj):
        """Check if saved item is still available"""
        try:
            if obj.variant_id:
                variant = ProductVariant.objects.get(
                    id=obj.variant_id, 
                    is_active=True,
                    product__is_active=True
                )
                return variant.is_in_stock
            else:
                product = Product.objects.get(id=obj.product_id, is_active=True)
                return product.is_in_stock
        except (Product.DoesNotExist, ProductVariant.DoesNotExist):
            return False


class MoveToCartSerializer(serializers.Serializer):
    """Move saved item to cart serializer"""
    
    saved_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1, max_value=100)
    
    def validate_saved_item_id(self, value):
        """Validate saved item exists"""
        user = self.context['request'].user
        try:
            SavedForLater.objects.get(id=value, user=user)
        except SavedForLater.DoesNotExist:
            raise serializers.ValidationError("Saved item not found.")
        return value


class CartSummarySerializer(serializers.Serializer):
    """Cart summary for checkout"""
    
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    items_count = serializers.IntegerField()
    total_weight = serializers.DecimalField(max_digits=8, decimal_places=3)
    
    # Coupon info
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    coupon_discount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    # Shipping info
    shipping_method = serializers.CharField(required=False, allow_blank=True)
    estimated_delivery = serializers.CharField(required=False, allow_blank=True)
