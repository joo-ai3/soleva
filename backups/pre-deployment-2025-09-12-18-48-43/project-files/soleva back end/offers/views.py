from rest_framework import status, permissions, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from django.db.models import Q, Prefetch
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from decimal import Decimal
import logging

from .models import FlashSale, SpecialOffer, OfferUsage, FlashSaleProduct
from .serializers import (
    FlashSaleSerializer, FlashSaleListSerializer, SpecialOfferSerializer,
    SpecialOfferListSerializer, OfferCalculationRequestSerializer,
    OfferCalculationResponseSerializer, OfferUsageSerializer,
    FlashSaleActivationSerializer, SpecialOfferActivationSerializer,
    ProductOfferCheckSerializer, ProductOfferResponseSerializer,
    FlashSaleProductSerializer
)

logger = logging.getLogger(__name__)


class FlashSaleViewSet(ReadOnlyModelViewSet):
    """Flash sale viewset for public access"""
    
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['display_priority', 'start_time', 'end_time']
    ordering = ['-display_priority', '-start_time']
    
    def get_queryset(self):
        """Get active flash sales"""
        now = timezone.now()
        return FlashSale.objects.filter(
            is_active=True
        ).prefetch_related(
            'products__product'
        ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FlashSaleListSerializer
        return FlashSaleSerializer
    
    def list(self, request, *args, **kwargs):
        """Get flash sales list with caching"""
        cache_key = 'flash_sales_list'
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            cached_data = serializer.data
            
            # Cache for 5 minutes
            cache.set(cache_key, cached_data, 300)
        
        return Response(cached_data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get currently running flash sales"""
        now = timezone.now()
        queryset = self.get_queryset().filter(
            start_time__lte=now,
            end_time__gte=now
        )
        
        serializer = FlashSaleListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming flash sales"""
        now = timezone.now()
        queryset = self.get_queryset().filter(
            start_time__gt=now
        )
        
        serializer = FlashSaleListSerializer(queryset, many=True)
        return Response(serializer.data)


class SpecialOfferViewSet(ReadOnlyModelViewSet):
    """Special offer viewset for public access"""
    
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['start_time', 'end_time', 'offer_type']
    ordering = ['-start_time']
    
    def get_queryset(self):
        """Get active special offers"""
        now = timezone.now()
        return SpecialOffer.objects.filter(
            is_active=True,
            start_time__lte=now
        ).filter(
            Q(end_time__isnull=True) | Q(end_time__gte=now)
        ).prefetch_related(
            'applicable_products',
            'applicable_categories'
        ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SpecialOfferListSerializer
        return SpecialOfferSerializer
    
    def list(self, request, *args, **kwargs):
        """Get special offers list with caching"""
        cache_key = 'special_offers_list'
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            cached_data = serializer.data
            
            # Cache for 5 minutes
            cache.set(cache_key, cached_data, 300)
        
        return Response(cached_data)
    
    @action(detail=False, methods=['get'])
    def for_product(self, request):
        """Get special offers applicable to a specific product"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {'error': 'product_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            Q(applicable_products__id=product_id) |
            Q(applicable_products__isnull=True, applicable_categories__isnull=True) |
            Q(applicable_categories__products__id=product_id)
        ).distinct()
        
        serializer = SpecialOfferListSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def calculate_offers(request):
    """Calculate available offers for a cart"""
    serializer = OfferCalculationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    cart_items = data['cart_items']
    user_id = data.get('user_id')
    
    try:
        # Get current offers
        now = timezone.now()
        
        # Get active flash sales
        flash_sales = FlashSale.objects.filter(
            is_active=True,
            start_time__lte=now,
            end_time__gte=now
        ).prefetch_related('products__product')
        
        # Get active special offers
        special_offers = SpecialOffer.objects.filter(
            is_active=True,
            start_time__lte=now
        ).filter(
            Q(end_time__isnull=True) | Q(end_time__gte=now)
        ).prefetch_related('applicable_products', 'applicable_categories')
        
        flash_sale_results = []
        special_offer_results = []
        
        # Calculate flash sale discounts
        for flash_sale in flash_sales:
            applicable_items = []
            total_discount = Decimal('0.00')
            
            for item in cart_items:
                product_id = item['product_id']
                quantity = int(item['quantity'])
                
                # Check if product is in flash sale
                flash_product = flash_sale.products.filter(
                    product_id=product_id
                ).first()
                
                if flash_product and flash_product.is_available:
                    available_qty = min(quantity, flash_product.remaining_quantity or quantity)
                    discount_per_item = flash_product.discount_amount
                    item_discount = discount_per_item * available_qty
                    total_discount += item_discount
                    
                    applicable_items.append({
                        'product_id': product_id,
                        'quantity': available_qty,
                        'discount_per_item': float(discount_per_item),
                        'total_discount': float(item_discount)
                    })
            
            if applicable_items:
                flash_sale_results.append({
                    'id': str(flash_sale.id),
                    'name_en': flash_sale.name_en,
                    'name_ar': flash_sale.name_ar,
                    'total_discount': float(total_discount),
                    'applicable_items': applicable_items,
                    'time_remaining': flash_sale.time_remaining
                })
        
        # Calculate special offer discounts
        for offer in special_offers:
            if user_id:
                can_use, reason = offer.can_be_used_by_customer(
                    user_id, 
                    OfferUsage.objects.filter(
                        special_offer=offer,
                        user_id=user_id
                    ).count()
                )
                if not can_use:
                    continue
            
            result = offer.calculate_discount(cart_items, sum(
                Decimal(str(item['price'])) * int(item['quantity']) 
                for item in cart_items
            ))
            
            if (result['discount_amount'] > 0 or 
                result['free_items'] or 
                result['free_shipping']):
                
                special_offer_results.append({
                    'id': str(offer.id),
                    'name_en': offer.name_en,
                    'name_ar': offer.name_ar,
                    'offer_type': offer.offer_type,
                    'discount_amount': float(result['discount_amount']),
                    'free_items': result['free_items'],
                    'free_shipping': result['free_shipping'],
                    'description': result['description'],
                    'time_remaining': offer.time_remaining,
                    'button_text_en': offer.button_text_en,
                    'button_text_ar': offer.button_text_ar,
                    'button_color': offer.button_color,
                    'highlight_color': offer.highlight_color
                })
        
        # Find best offer
        all_offers = flash_sale_results + special_offer_results
        best_offer = None
        max_discount = Decimal('0.00')
        
        for offer in all_offers:
            discount = Decimal(str(offer.get('total_discount', offer.get('discount_amount', 0))))
            if discount > max_discount:
                max_discount = discount
                best_offer = offer
        
        # Check if any offers provide free shipping
        free_shipping_available = any(
            offer.get('free_shipping', False) 
            for offer in special_offer_results
        )
        
        # Coupons are blocked if any offers are available
        coupons_blocked = bool(all_offers)
        
        response_data = {
            'flash_sales': flash_sale_results,
            'special_offers': special_offer_results,
            'best_offer': best_offer,
            'total_discount': float(max_discount),
            'free_shipping_available': free_shipping_available,
            'coupons_blocked': coupons_blocked
        }
        
        response_serializer = OfferCalculationResponseSerializer(response_data)
        return Response(response_serializer.data)
        
    except Exception as e:
        logger.error(f"Error calculating offers: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def check_product_offers(request):
    """Check offers available for a specific product"""
    serializer = ProductOfferCheckSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    product_id = data['product_id']
    quantity = data['quantity']
    user_id = data.get('user_id')
    
    try:
        now = timezone.now()
        
        # Check flash sales
        flash_sale_product = None
        flash_sales = FlashSale.objects.filter(
            is_active=True,
            start_time__lte=now,
            end_time__gte=now,
            products__product_id=product_id
        ).prefetch_related('products').first()
        
        if flash_sales:
            flash_sale_product = flash_sales.products.filter(
                product_id=product_id
            ).first()
        
        # Check special offers
        special_offers = SpecialOffer.objects.filter(
            is_active=True,
            start_time__lte=now,
            show_on_product_page=True
        ).filter(
            Q(end_time__isnull=True) | Q(end_time__gte=now)
        ).filter(
            Q(applicable_products__id=product_id) |
            Q(applicable_products__isnull=True, applicable_categories__isnull=True) |
            Q(applicable_categories__products__id=product_id)
        ).distinct()
        
        # Filter by user eligibility if user provided
        eligible_offers = []
        for offer in special_offers:
            if user_id:
                can_use, _ = offer.can_be_used_by_customer(
                    user_id,
                    OfferUsage.objects.filter(
                        special_offer=offer,
                        user_id=user_id
                    ).count()
                )
                if not can_use:
                    continue
            eligible_offers.append(offer)
        
        # Calculate best discount
        best_discount = None
        if flash_sale_product and flash_sale_product.is_available:
            best_discount = float(flash_sale_product.discount_amount * quantity)
        
        for offer in eligible_offers:
            cart_items = [{
                'product_id': str(product_id),
                'quantity': quantity,
                'price': '100'  # Dummy price for calculation
            }]
            result = offer.calculate_discount(cart_items, Decimal('100') * quantity)
            
            if result['discount_amount'] > 0:
                discount = float(result['discount_amount'])
                if best_discount is None or discount > best_discount:
                    best_discount = discount
        
        response_data = {
            'flash_sale': FlashSaleProductSerializer(flash_sale_product).data if flash_sale_product else None,
            'special_offers': SpecialOfferListSerializer(eligible_offers, many=True).data,
            'best_discount': best_discount,
            'has_active_offers': bool(flash_sale_product or eligible_offers)
        }
        
        response_serializer = ProductOfferResponseSerializer(response_data)
        return Response(response_serializer.data)
        
    except Exception as e:
        logger.error(f"Error checking product offers: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def activate_flash_sale(request, pk):
    """Activate or deactivate a flash sale"""
    try:
        flash_sale = FlashSale.objects.get(pk=pk)
    except FlashSale.DoesNotExist:
        return Response(
            {'error': 'Flash sale not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = FlashSaleActivationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    flash_sale.is_active = serializer.validated_data['is_active']
    flash_sale.save()
    
    # Clear cache
    cache.delete('flash_sales_list')
    
    return Response({
        'message': f'Flash sale {"activated" if flash_sale.is_active else "deactivated"} successfully',
        'is_active': flash_sale.is_active
    })


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def activate_special_offer(request, pk):
    """Activate or deactivate a special offer"""
    try:
        special_offer = SpecialOffer.objects.get(pk=pk)
    except SpecialOffer.DoesNotExist:
        return Response(
            {'error': 'Special offer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = SpecialOfferActivationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    special_offer.is_active = serializer.validated_data['is_active']
    special_offer.save()
    
    # Clear cache
    cache.delete('special_offers_list')
    
    return Response({
        'message': f'Special offer {"activated" if special_offer.is_active else "deactivated"} successfully',
        'is_active': special_offer.is_active
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def record_offer_usage(request):
    """Record offer usage (called when order is placed)"""
    data = request.data
    
    try:
        with transaction.atomic():
            usage_data = {
                'user_id': data.get('user_id'),
                'order_id': data.get('order_id'),
                'discount_amount': Decimal(str(data.get('discount_amount', 0))),
                'free_shipping_applied': data.get('free_shipping_applied', False),
                'free_items_json': data.get('free_items', []),
                'order_total': Decimal(str(data.get('order_total', 0)))
            }
            
            # Record flash sale usage
            if data.get('flash_sale_id'):
                flash_sale = FlashSale.objects.get(id=data['flash_sale_id'])
                usage_data['flash_sale'] = flash_sale
                
                # Update usage count
                flash_sale.current_usage_count += 1
                flash_sale.save()
                
                # Update sold quantities for flash sale products
                for item in data.get('flash_sale_items', []):
                    flash_product = FlashSaleProduct.objects.get(
                        flash_sale=flash_sale,
                        product_id=item['product_id']
                    )
                    flash_product.sold_quantity += item['quantity']
                    flash_product.save()
            
            # Record special offer usage
            if data.get('special_offer_id'):
                special_offer = SpecialOffer.objects.get(id=data['special_offer_id'])
                usage_data['special_offer'] = special_offer
                
                # Update usage count
                special_offer.current_usage_count += 1
                special_offer.save()
            
            # Create usage record
            OfferUsage.objects.create(**usage_data)
            
            return Response({'message': 'Offer usage recorded successfully'})
            
    except Exception as e:
        logger.error(f"Error recording offer usage: {str(e)}")
        return Response(
            {'error': 'Failed to record offer usage'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def offer_analytics(request):
    """Get offer analytics (admin only)"""
    now = timezone.now()
    
    analytics = {
        'flash_sales': {
            'total': FlashSale.objects.count(),
            'active': FlashSale.objects.filter(is_active=True).count(),
            'running': FlashSale.objects.filter(
                is_active=True,
                start_time__lte=now,
                end_time__gte=now
            ).count(),
            'upcoming': FlashSale.objects.filter(
                is_active=True,
                start_time__gt=now
            ).count(),
        },
        'special_offers': {
            'total': SpecialOffer.objects.count(),
            'active': SpecialOffer.objects.filter(is_active=True).count(),
            'running': SpecialOffer.objects.filter(
                is_active=True,
                start_time__lte=now
            ).filter(
                Q(end_time__isnull=True) | Q(end_time__gte=now)
            ).count(),
        },
        'usage_stats': {
            'total_usage': OfferUsage.objects.count(),
            'this_month': OfferUsage.objects.filter(
                created_at__month=now.month,
                created_at__year=now.year
            ).count(),
            'total_discount_given': float(
                OfferUsage.objects.aggregate(
                    total=models.Sum('discount_amount')
                )['total'] or 0
            ),
        }
    }
    
    return Response(analytics)
