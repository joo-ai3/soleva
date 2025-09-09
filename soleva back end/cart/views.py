from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from decimal import Decimal

from .models import Cart, CartItem, SavedForLater
from .serializers import (
    CartSerializer, CartItemSerializer, AddToCartSerializer,
    SavedForLaterSerializer, MoveToCartSerializer, CartSummarySerializer
)
from products.models import Product, ProductVariant
from coupons.models import Coupon

User = get_user_model()


class CartView(APIView):
    """Cart management view"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user's cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)
    
    def delete(self, request):
        """Clear cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.clear()
        return Response({
            'message': 'Cart cleared successfully.'
        }, status=status.HTTP_200_OK)


class AddToCartView(APIView):
    """Add item to cart"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Add item to cart"""
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product']
            variant = serializer.validated_data.get('variant')
            quantity = serializer.validated_data['quantity']
            
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            with transaction.atomic():
                # Check if item already exists in cart
                cart_item_kwargs = {
                    'cart': cart,
                    'product_id': product.id,
                    'variant_id': variant.id if variant else None,
                }
                
                cart_item, item_created = CartItem.objects.get_or_create(
                    **cart_item_kwargs,
                    defaults={
                        'quantity': quantity,
                        'product_name': product.name_en,
                        'product_price': variant.effective_price if variant else product.price,
                        'product_image': variant.image.url if variant and variant.image else (
                            product.images.filter(is_primary=True).first().image.url 
                            if product.images.filter(is_primary=True).exists() else ''
                        ),
                        'variant_attributes': self._get_variant_attributes(variant) if variant else {},
                    }
                )
                
                if not item_created:
                    # Update quantity if item already exists
                    new_quantity = cart_item.quantity + quantity
                    
                    # Check stock availability for new quantity
                    if variant:
                        if variant.inventory_quantity < new_quantity:
                            return Response({
                                'error': f'Only {variant.inventory_quantity} items available. You currently have {cart_item.quantity} in cart.'
                            }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        if product.track_inventory and product.inventory_quantity < new_quantity:
                            return Response({
                                'error': f'Only {product.inventory_quantity} items available. You currently have {cart_item.quantity} in cart.'
                            }, status=status.HTTP_400_BAD_REQUEST)
                    
                    cart_item.quantity = new_quantity
                    cart_item.save()
            
            # Return updated cart
            cart_serializer = CartSerializer(cart, context={'request': request})
            return Response({
                'message': 'Item added to cart successfully.',
                'cart': cart_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_variant_attributes(self, variant):
        """Get variant attributes as dictionary"""
        if not variant:
            return {}
        
        attributes = {}
        for va in variant.attribute_values.select_related('attribute', 'value'):
            attributes[va.attribute.name_en] = va.value.value_en
        return attributes


class CartItemViewSet(ModelViewSet):
    """Cart item management"""
    
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get cart items for current user"""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart.items.all().order_by('-created_at')
    
    def update(self, request, *args, **kwargs):
        """Update cart item quantity"""
        cart_item = self.get_object()
        
        # Only allow updating quantity
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response({
                'error': 'Quantity is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response({
                    'error': 'Quantity must be greater than 0.'
                }, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({
                'error': 'Invalid quantity value.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check stock availability
        if cart_item.variant_id:
            try:
                variant = ProductVariant.objects.get(
                    id=cart_item.variant_id, 
                    is_active=True
                )
                if variant.inventory_quantity < quantity:
                    return Response({
                        'error': f'Only {variant.inventory_quantity} items available.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except ProductVariant.DoesNotExist:
                return Response({
                    'error': 'Product variant no longer available.'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                product = Product.objects.get(
                    id=cart_item.product_id, 
                    is_active=True
                )
                if product.track_inventory and product.inventory_quantity < quantity:
                    return Response({
                        'error': f'Only {product.inventory_quantity} items available.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Product.DoesNotExist:
                return Response({
                    'error': 'Product no longer available.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item.quantity = quantity
        cart_item.save()
        
        serializer = self.get_serializer(cart_item)
        return Response({
            'message': 'Cart item updated successfully.',
            'item': serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """Remove item from cart"""
        cart_item = self.get_object()
        cart_item.delete()
        return Response({
            'message': 'Item removed from cart successfully.'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def save_for_later(self, request, pk=None):
        """Move item to saved for later"""
        cart_item = self.get_object()
        
        # Create saved for later item
        saved_item, created = SavedForLater.objects.get_or_create(
            user=request.user,
            product_id=cart_item.product_id,
            variant_id=cart_item.variant_id,
            defaults={
                'product_name': cart_item.product_name,
                'product_price': cart_item.product_price,
                'product_image': cart_item.product_image,
                'variant_attributes': cart_item.variant_attributes,
            }
        )
        
        # Remove from cart
        cart_item.delete()
        
        return Response({
            'message': 'Item moved to saved for later successfully.',
            'saved_item': SavedForLaterSerializer(saved_item, context={'request': request}).data
        })


class SavedForLaterViewSet(ModelViewSet):
    """Saved for later management"""
    
    serializer_class = SavedForLaterSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get saved items for current user"""
        return SavedForLater.objects.filter(user=self.request.user).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Save item for later"""
        product_id = request.data.get('product_id')
        variant_id = request.data.get('variant_id')
        
        if not product_id:
            return Response({
                'error': 'Product ID is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({
                'error': 'Product not found.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        variant = None
        if variant_id:
            try:
                variant = ProductVariant.objects.get(
                    id=variant_id, 
                    product=product, 
                    is_active=True
                )
            except ProductVariant.DoesNotExist:
                return Response({
                    'error': 'Product variant not found.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create saved item
        saved_item, created = SavedForLater.objects.get_or_create(
            user=request.user,
            product_id=product.id,
            variant_id=variant.id if variant else None,
            defaults={
                'product_name': product.name_en,
                'product_price': variant.effective_price if variant else product.price,
                'product_image': variant.image.url if variant and variant.image else (
                    product.images.filter(is_primary=True).first().image.url 
                    if product.images.filter(is_primary=True).exists() else ''
                ),
                'variant_attributes': self._get_variant_attributes(variant) if variant else {},
            }
        )
        
        if not created:
            return Response({
                'message': 'Item already saved for later.',
                'saved_item': SavedForLaterSerializer(saved_item, context={'request': request}).data
            })
        
        return Response({
            'message': 'Item saved for later successfully.',
            'saved_item': SavedForLaterSerializer(saved_item, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    def _get_variant_attributes(self, variant):
        """Get variant attributes as dictionary"""
        if not variant:
            return {}
        
        attributes = {}
        for va in variant.attribute_values.select_related('attribute', 'value'):
            attributes[va.attribute.name_en] = va.value.value_en
        return attributes
    
    @action(detail=True, methods=['post'])
    def move_to_cart(self, request, pk=None):
        """Move saved item to cart"""
        saved_item = self.get_object()
        serializer = MoveToCartSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            
            # Check if product/variant is still available
            try:
                if saved_item.variant_id:
                    variant = ProductVariant.objects.get(
                        id=saved_item.variant_id, 
                        is_active=True,
                        product__is_active=True
                    )
                    if variant.inventory_quantity < quantity:
                        return Response({
                            'error': f'Only {variant.inventory_quantity} items available.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    product = Product.objects.get(
                        id=saved_item.product_id, 
                        is_active=True
                    )
                    if product.track_inventory and product.inventory_quantity < quantity:
                        return Response({
                            'error': f'Only {product.inventory_quantity} items available.'
                        }, status=status.HTTP_400_BAD_REQUEST)
            except (Product.DoesNotExist, ProductVariant.DoesNotExist):
                return Response({
                    'error': 'Item is no longer available.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Add to cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            cart_item_kwargs = {
                'cart': cart,
                'product_id': saved_item.product_id,
                'variant_id': saved_item.variant_id,
            }
            
            cart_item, item_created = CartItem.objects.get_or_create(
                **cart_item_kwargs,
                defaults={
                    'quantity': quantity,
                    'product_name': saved_item.product_name,
                    'product_price': saved_item.product_price,
                    'product_image': saved_item.product_image,
                    'variant_attributes': saved_item.variant_attributes,
                }
            )
            
            if not item_created:
                cart_item.quantity += quantity
                cart_item.save()
            
            # Remove from saved items
            saved_item.delete()
            
            return Response({
                'message': 'Item moved to cart successfully.',
                'cart_item': CartItemSerializer(cart_item, context={'request': request}).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def apply_coupon(request):
    """Apply coupon to cart"""
    coupon_code = request.data.get('coupon_code', '').strip().upper()
    
    if not coupon_code:
        return Response({
            'error': 'Coupon code is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        coupon = Coupon.objects.get(code=coupon_code, is_active=True)
    except Coupon.DoesNotExist:
        return Response({
            'error': 'Invalid coupon code.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_total = cart.subtotal
    
    # Validate coupon
    can_use, message = coupon.can_be_used_by_customer(request.user, cart_total)
    if not can_use:
        return Response({
            'error': message
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate discount
    discount_amount = coupon.calculate_discount(cart_total)
    
    return Response({
        'message': 'Coupon applied successfully.',
        'coupon': {
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'discount_amount': discount_amount,
        },
        'cart_total': cart_total,
        'discount_amount': discount_amount,
        'final_total': cart_total - discount_amount,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def cart_summary(request):
    """Get cart summary for checkout"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if not cart.items.exists():
        return Response({
            'error': 'Cart is empty.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate totals
    subtotal = cart.subtotal
    items_count = cart.total_items
    
    # Calculate total weight (for shipping)
    total_weight = Decimal('0.000')
    for item in cart.items.all():
        try:
            if item.variant_id:
                variant = ProductVariant.objects.get(id=item.variant_id)
                weight = variant.weight or variant.product.weight or Decimal('0.500')  # Default 500g
            else:
                product = Product.objects.get(id=item.product_id)
                weight = product.weight or Decimal('0.500')  # Default 500g
            
            total_weight += weight * item.quantity
        except (Product.DoesNotExist, ProductVariant.DoesNotExist):
            continue
    
    # For now, set default values (will be calculated properly with shipping/coupon integration)
    shipping_cost = Decimal('30.00')  # Default shipping cost
    tax_amount = Decimal('0.00')      # No tax for now
    discount_amount = Decimal('0.00')  # No discount for now
    
    total = subtotal + shipping_cost + tax_amount - discount_amount
    
    summary_data = {
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'tax_amount': tax_amount,
        'discount_amount': discount_amount,
        'total': total,
        'items_count': items_count,
        'total_weight': total_weight,
    }
    
    serializer = CartSummarySerializer(summary_data)
    return Response(serializer.data)
