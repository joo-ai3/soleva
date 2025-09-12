from rest_framework import status, permissions, generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Q
from django.core.cache import cache
from django.utils import timezone
from decimal import Decimal

from .models import Coupon, CouponUsage
from .serializers import (
    CouponSerializer, CouponCreateUpdateSerializer,
    CouponUsageSerializer, CouponValidationSerializer
)


def check_active_offers_block_coupons(cart_items):
    """Check if there are active offers that would block coupon usage"""
    if not cart_items:
        return False
    
    try:
        from offers.models import FlashSale, SpecialOffer, FlashSaleProduct
        from django.utils import timezone
        
        now = timezone.now()
        
        # Get product IDs from cart
        product_ids = [str(item.get('product_id', '')) for item in cart_items if item.get('product_id')]
        
        if not product_ids:
            return False
        
        # Check for active flash sales with products in cart
        flash_sales_with_products = FlashSale.objects.filter(
            is_active=True,
            start_time__lte=now,
            end_time__gte=now,
            products__product_id__in=product_ids,
            products__is_available=True
        ).exists()
        
        if flash_sales_with_products:
            return True
        
        # Check for active special offers applicable to cart products
        special_offers = SpecialOffer.objects.filter(
            is_active=True,
            start_time__lte=now,
            show_on_product_page=True
        ).filter(
            Q(end_time__isnull=True) | Q(end_time__gte=now)
        )
        
        for offer in special_offers:
            # Check if offer applies to any cart products
            if offer.applicable_products.filter(id__in=product_ids).exists():
                return True
            
            # Check if offer applies through categories
            if offer.applicable_categories.exists():
                from products.models import Product
                cart_products = Product.objects.filter(id__in=product_ids)
                cart_category_ids = list(cart_products.values_list('category_id', flat=True))
                
                if offer.applicable_categories.filter(id__in=cart_category_ids).exists():
                    return True
            
            # If no specific products or categories, offer applies to all
            if not offer.applicable_products.exists() and not offer.applicable_categories.exists():
                return True
        
        return False
        
    except ImportError:
        # If offers app is not available, don't block coupons
        return False
    except Exception as e:
        # Log error but don't block coupons due to unexpected errors
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error checking offers for coupon blocking: {str(e)}")
        return False

User = get_user_model()


class CouponListView(generics.ListAPIView):
    """List all active coupons (admin only)"""
    
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name_en', 'name_ar']
    ordering_fields = ['created_at', 'valid_from', 'valid_until', 'usage_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get coupons with usage statistics"""
        return Coupon.objects.all().annotate(
            usage_count=Count('usage_records')
        )


class CouponCreateView(generics.CreateAPIView):
    """Create new coupon (admin only)"""
    
    serializer_class = CouponCreateUpdateSerializer
    permission_classes = [permissions.IsAdminUser]


class CouponDetailView(generics.RetrieveAPIView):
    """Get coupon details (admin only)"""
    
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Coupon.objects.all()


class CouponUpdateView(generics.UpdateAPIView):
    """Update coupon (admin only)"""
    
    serializer_class = CouponCreateUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Coupon.objects.all()


class CouponDeleteView(generics.DestroyAPIView):
    """Delete coupon (admin only)"""
    
    permission_classes = [permissions.IsAdminUser]
    queryset = Coupon.objects.all()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def validate_coupon(request):
    """Validate coupon code"""
    serializer = CouponValidationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    coupon_code = serializer.validated_data['code']
    cart_total = serializer.validated_data.get('cart_total', Decimal('0.00'))
    cart_items = request.data.get('cart_items', [])
    
    # Check if offers are active that would block coupons
    offers_blocked = check_active_offers_block_coupons(cart_items)
    if offers_blocked:
        return Response({
            'valid': False,
            'error': 'Coupons cannot be applied while special offers or flash sales are active on your cart items.',
            'blocked_by_offers': True
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        coupon = Coupon.objects.get(code=coupon_code.upper(), is_active=True)
    except Coupon.DoesNotExist:
        return Response({
            'valid': False,
            'error': 'Invalid coupon code.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if coupon is valid for current user
    user = request.user if request.user.is_authenticated else None
    can_use, message = coupon.can_be_used_by_customer(user, cart_total)
    
    if not can_use:
        return Response({
            'valid': False,
            'error': message
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate discount
    discount_amount = coupon.calculate_discount(cart_total)
    
    return Response({
        'valid': True,
        'coupon': {
            'id': coupon.id,
            'code': coupon.code,
            'name': coupon.name_en,
            'description': coupon.description_en,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'max_discount_amount': coupon.max_discount_amount,
            'minimum_order_amount': coupon.minimum_order_amount,
            'discount_amount': discount_amount,
            'free_shipping': coupon.free_shipping,
            'valid_until': coupon.valid_until,
        }
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def apply_coupon(request):
    """Apply coupon to user's cart"""
    coupon_code = request.data.get('code', '').strip().upper()
    cart_items = request.data.get('cart_items', [])
    
    if not coupon_code:
        return Response({
            'error': 'Coupon code is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if offers are active that would block coupons
    offers_blocked = check_active_offers_block_coupons(cart_items)
    if offers_blocked:
        return Response({
            'error': 'Coupons cannot be applied while special offers or flash sales are active on your cart items.',
            'blocked_by_offers': True
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        coupon = Coupon.objects.get(code=coupon_code, is_active=True)
    except Coupon.DoesNotExist:
        return Response({
            'error': 'Invalid coupon code.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get cart total (this would normally come from cart service)
    cart_total = request.data.get('cart_total', Decimal('0.00'))
    
    # Validate coupon
    can_use, message = coupon.can_be_used_by_customer(request.user, cart_total)
    if not can_use:
        return Response({
            'error': message
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate discount
    discount_amount = coupon.calculate_discount(cart_total)
    
    # Record coupon usage (this would be done during order creation)
    # CouponUsage.objects.create(
    #     coupon=coupon,
    #     user=request.user,
    #     order_total=cart_total,
    #     discount_amount=discount_amount
    # )
    
    return Response({
        'message': 'Coupon applied successfully.',
        'coupon': {
            'id': coupon.id,
            'code': coupon.code,
            'name': coupon.name_en,
            'description': coupon.description_en,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'discount_amount': discount_amount,
            'free_shipping': coupon.free_shipping,
        },
        'cart_total': cart_total,
        'discount_amount': discount_amount,
        'final_total': max(cart_total - discount_amount, Decimal('0.00')),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def coupon_stats(request):
    """Get coupon usage statistics (admin only)"""
    cache_key = 'coupon_stats'
    stats = cache.get(cache_key)
    
    if not stats:
        total_coupons = Coupon.objects.count()
        active_coupons = Coupon.objects.filter(is_active=True).count()
        expired_coupons = Coupon.objects.filter(
            valid_until__lt=timezone.now().date(),
            is_active=True
        ).count()
        
        # Usage statistics
        total_usage = CouponUsage.objects.count()
        total_discount_given = CouponUsage.objects.aggregate(
            total=Sum('discount_amount')
        )['total'] or Decimal('0.00')
        
        # Most used coupons
        most_used = Coupon.objects.annotate(
            usage_count=Count('usage_records')
        ).filter(usage_count__gt=0).order_by('-usage_count')[:10]
        
        # Recent usage
        recent_usage = CouponUsage.objects.select_related(
            'coupon', 'user'
        ).order_by('-created_at')[:20]
        
        stats = {
            'total_coupons': total_coupons,
            'active_coupons': active_coupons,
            'expired_coupons': expired_coupons,
            'total_usage': total_usage,
            'total_discount_given': float(total_discount_given),
            'most_used_coupons': [
                {
                    'id': coupon.id,
                    'code': coupon.code,
                    'name': coupon.name_en,
                    'usage_count': coupon.usage_count,
                    'discount_type': coupon.discount_type,
                    'discount_value': float(coupon.discount_value),
                }
                for coupon in most_used
            ],
            'recent_usage': [
                {
                    'id': usage.id,
                    'coupon_code': usage.coupon.code,
                    'user_email': usage.user.email if usage.user else 'Guest',
                    'order_total': float(usage.order_total),
                    'discount_amount': float(usage.discount_amount),
                    'created_at': usage.created_at.isoformat(),
                }
                for usage in recent_usage
            ]
        }
        
        # Cache for 15 minutes
        cache.set(cache_key, stats, 900)
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def coupon_usage(request, pk):
    """Get usage history for specific coupon (admin only)"""
    try:
        coupon = Coupon.objects.get(pk=pk)
    except Coupon.DoesNotExist:
        return Response({
            'error': 'Coupon not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    usage_records = coupon.usage_records.select_related('user').order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(usage_records, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    usage_data = []
    for usage in page_obj:
        usage_data.append({
            'id': usage.id,
            'user': {
                'id': usage.user.id if usage.user else None,
                'email': usage.user.email if usage.user else 'Guest',
                'full_name': usage.user.full_name if usage.user else 'Guest User',
            },
            'order_id': usage.order_id,
            'order_total': float(usage.order_total),
            'discount_amount': float(usage.discount_amount),
            'created_at': usage.created_at.isoformat(),
        })
    
    return Response({
        'coupon': {
            'id': coupon.id,
            'code': coupon.code,
            'name': coupon.name_en,
            'description': coupon.description_en,
        },
        'usage_records': usage_data,
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_records': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    })
