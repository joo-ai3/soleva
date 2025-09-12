from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta, date
from decimal import Decimal

from .models import TrackingPixel, TrackingEvent, ConversionTracking, AbandonedCart
from .serializers import (
    TrackingPixelSerializer, TrackingEventSerializer, TrackEventSerializer,
    ConversionTrackingSerializer, AbandonedCartSerializer, PixelConfigSerializer,
    ConversionFunnelSerializer, TrackingStatsSerializer, UTMParametersSerializer
)


class TrackingPixelListView(generics.ListCreateAPIView):
    """Tracking pixel management (admin only)"""
    
    queryset = TrackingPixel.objects.all()
    serializer_class = TrackingPixelSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get('active_only') == 'true':
            queryset = queryset.filter(is_active=True)
        return queryset


class TrackEventView(APIView):
    """Track events endpoint"""
    
    permission_classes = [permissions.AllowAny]  # Allow anonymous tracking
    
    def post(self, request):
        """Track an event"""
        serializer = TrackEventSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Get user info
        user = request.user if request.user.is_authenticated else None
        
        # Get request metadata
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Get or create session ID
        session_id = data.get('session_id') or request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        # Get active pixels to track
        pixel_types = data.get('pixel_types', [])
        if not pixel_types:
            # Track on all active pixels if none specified
            pixels = TrackingPixel.objects.filter(is_active=True, track_ecommerce=True)
        else:
            pixels = TrackingPixel.objects.filter(
                is_active=True,
                pixel_type__in=pixel_types
            )
        
        # Create tracking events
        events_created = []
        for pixel in pixels:
            event = TrackingEvent.objects.create(
                event_name=data['event_name'],
                event_type=data['event_type'],
                user=user,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=data.get('referrer', ''),
                page_url=data.get('page_url', ''),
                event_data=data.get('event_data', {}),
                product_id=data.get('product_id', ''),
                product_name=data.get('product_name', ''),
                product_category=data.get('product_category', ''),
                product_price=data.get('product_price'),
                quantity=data.get('quantity'),
                value=data.get('value'),
                currency=data.get('currency', 'EGP'),
                order_id=data.get('order_id', ''),
                pixel=pixel
            )
            events_created.append(event)
        
        # Update conversion tracking
        self.update_conversion_tracking(request, data, session_id, user)
        
        # Check for abandoned cart
        if data['event_type'] == 'add_to_cart' and user:
            self.check_abandoned_cart(user, session_id, data)
        
        return Response({
            'message': f'Event tracked successfully on {len(events_created)} pixels.',
            'events_created': len(events_created),
            'session_id': session_id
        }, status=status.HTTP_201_CREATED)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def update_conversion_tracking(self, request, data, session_id, user):
        """Update conversion tracking funnel"""
        try:
            # Get or create conversion tracking record
            conversion, created = ConversionTracking.objects.get_or_create(
                session_id=session_id,
                defaults={
                    'user': user,
                    'utm_source': request.GET.get('utm_source', ''),
                    'utm_medium': request.GET.get('utm_medium', ''),
                    'utm_campaign': request.GET.get('utm_campaign', ''),
                    'utm_term': request.GET.get('utm_term', ''),
                    'utm_content': request.GET.get('utm_content', ''),
                    'referrer': data.get('referrer', ''),
                }
            )
            
            # Update funnel step timestamps
            now = timezone.now()
            event_type = data['event_type']
            
            if event_type == 'page_view' and not conversion.landing_at:
                conversion.landing_at = now
            elif event_type == 'view_content' and not conversion.product_view_at:
                conversion.product_view_at = now
                if data.get('product_name') and not conversion.first_product_viewed:
                    conversion.first_product_viewed = data['product_name']
                
                # Add to viewed products list
                products_viewed = conversion.products_viewed or []
                if data.get('product_name') and data['product_name'] not in products_viewed:
                    products_viewed.append(data['product_name'])
                    conversion.products_viewed = products_viewed
                    
            elif event_type == 'add_to_cart' and not conversion.add_to_cart_at:
                conversion.add_to_cart_at = now
                if data.get('value'):
                    conversion.cart_value = data['value']
                    
            elif event_type == 'initiate_checkout' and not conversion.checkout_start_at:
                conversion.checkout_start_at = now
                
            elif event_type == 'add_payment_info' and not conversion.payment_info_at:
                conversion.payment_info_at = now
                
            elif event_type == 'purchase' and not conversion.purchase_at:
                conversion.purchase_at = now
                if data.get('value'):
                    conversion.order_value = data['value']
                if data.get('order_id'):
                    conversion.order_id = data['order_id']
            
            conversion.save()
            
        except Exception:
            # Don't fail the main request if conversion tracking fails
            pass
    
    def check_abandoned_cart(self, user, session_id, data):
        """Check and create abandoned cart record"""
        try:
            # Create or update abandoned cart
            abandoned_cart, created = AbandonedCart.objects.get_or_create(
                user=user,
                session_id=session_id,
                is_recovered=False,
                defaults={
                    'cart_items': [],
                    'cart_value': Decimal('0.00')
                }
            )
            
            # Update cart value
            if data.get('value'):
                abandoned_cart.cart_value = data['value']
                abandoned_cart.save()
                
        except Exception:
            # Don't fail the main request
            pass


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_pixel_config(request):
    """Get pixel configuration for frontend"""
    cache_key = 'pixel_config'
    config = cache.get(cache_key)
    
    if not config:
        # Get active pixels
        pixels = TrackingPixel.objects.filter(is_active=True)
        
        config = {
            'facebook_pixel_id': getattr(settings, 'FACEBOOK_PIXEL_ID', ''),
            'google_analytics_id': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
            'tiktok_pixel_id': getattr(settings, 'TIKTOK_PIXEL_ID', ''),
            'snapchat_pixel_id': getattr(settings, 'SNAPCHAT_PIXEL_ID', ''),
            'custom_pixels': []
        }
        
        # Add database-configured pixels
        for pixel in pixels:
            if pixel.pixel_type == 'facebook' and pixel.pixel_id:
                config['facebook_pixel_id'] = pixel.pixel_id
            elif pixel.pixel_type == 'google_analytics' and pixel.pixel_id:
                config['google_analytics_id'] = pixel.pixel_id
            elif pixel.pixel_type == 'tiktok' and pixel.pixel_id:
                config['tiktok_pixel_id'] = pixel.pixel_id
            elif pixel.pixel_type == 'snapchat' and pixel.pixel_id:
                config['snapchat_pixel_id'] = pixel.pixel_id
            elif pixel.pixel_type == 'custom':
                config['custom_pixels'].append({
                    'name': pixel.name,
                    'head_code': pixel.head_code,
                    'body_code': pixel.body_code,
                })
        
        # Cache for 30 minutes
        cache.set(cache_key, config, 1800)
    
    serializer = PixelConfigSerializer(config)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def conversion_funnel(request):
    """Get conversion funnel analytics"""
    # Get date range
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Get conversion data
    conversions = ConversionTracking.objects.filter(created_at__gte=start_date)
    
    total_sessions = conversions.count()
    landing_page = conversions.filter(landing_at__isnull=False).count()
    product_views = conversions.filter(product_view_at__isnull=False).count()
    add_to_cart = conversions.filter(add_to_cart_at__isnull=False).count()
    checkout_start = conversions.filter(checkout_start_at__isnull=False).count()
    payment_info = conversions.filter(payment_info_at__isnull=False).count()
    purchases = conversions.filter(purchase_at__isnull=False).count()
    
    # Calculate conversion rates
    def safe_divide(a, b):
        return (a / b * 100) if b > 0 else 0
    
    funnel_data = {
        'total_sessions': total_sessions,
        'landing_page': landing_page,
        'product_views': product_views,
        'add_to_cart': add_to_cart,
        'checkout_start': checkout_start,
        'payment_info': payment_info,
        'purchases': purchases,
        'landing_to_product_rate': safe_divide(product_views, landing_page),
        'product_to_cart_rate': safe_divide(add_to_cart, product_views),
        'cart_to_checkout_rate': safe_divide(checkout_start, add_to_cart),
        'checkout_to_payment_rate': safe_divide(payment_info, checkout_start),
        'payment_to_purchase_rate': safe_divide(purchases, payment_info),
        'overall_conversion_rate': safe_divide(purchases, total_sessions),
    }
    
    serializer = ConversionFunnelSerializer(funnel_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def tracking_stats(request):
    """Get tracking statistics"""
    # Get date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Get event counts
    all_events = TrackingEvent.objects.all()
    total_events = all_events.count()
    page_views = all_events.filter(event_type='page_view').count()
    product_views = all_events.filter(event_type='view_content').count()
    add_to_cart_events = all_events.filter(event_type='add_to_cart').count()
    purchase_events = all_events.filter(event_type='purchase').count()
    
    # Time-based counts
    today_events = all_events.filter(created_at__date=today).count()
    week_events = all_events.filter(created_at__date__gte=week_ago).count()
    month_events = all_events.filter(created_at__date__gte=month_ago).count()
    
    # Conversion data
    conversions = ConversionTracking.objects.all()
    total_conversions = conversions.filter(purchase_at__isnull=False).count()
    conversion_rate = (total_conversions / total_events * 100) if total_events > 0 else 0
    
    # Average order value
    purchase_values = all_events.filter(
        event_type='purchase',
        value__isnull=False
    ).aggregate(avg_value=Avg('value'))
    average_order_value = purchase_values['avg_value'] or Decimal('0.00')
    
    # Abandoned cart data
    abandoned_carts = AbandonedCart.objects.count()
    recovered_carts = AbandonedCart.objects.filter(is_recovered=True).count()
    cart_recovery_rate = (recovered_carts / abandoned_carts * 100) if abandoned_carts > 0 else 0
    
    # Top traffic sources
    top_sources = conversions.values('utm_source').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Top products
    top_products = all_events.filter(
        event_type='view_content',
        product_name__isnull=False
    ).values('product_name').annotate(
        views=Count('id')
    ).order_by('-views')[:10]
    
    stats_data = {
        'total_events': total_events,
        'page_views': page_views,
        'product_views': product_views,
        'add_to_cart_events': add_to_cart_events,
        'purchase_events': purchase_events,
        'total_conversions': total_conversions,
        'conversion_rate': conversion_rate,
        'average_order_value': average_order_value,
        'abandoned_carts': abandoned_carts,
        'recovered_carts': recovered_carts,
        'cart_recovery_rate': cart_recovery_rate,
        'today_events': today_events,
        'week_events': week_events,
        'month_events': month_events,
        'top_traffic_sources': list(top_sources),
        'top_products': list(top_products),
    }
    
    serializer = TrackingStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def abandoned_cart_list(request):
    """Get abandoned carts list"""
    abandoned_carts = AbandonedCart.objects.filter(
        is_recovered=False
    ).select_related('user').order_by('-created_at')
    
    # Filter by date if provided
    days = request.GET.get('days')
    if days:
        start_date = timezone.now() - timedelta(days=int(days))
        abandoned_carts = abandoned_carts.filter(created_at__gte=start_date)
    
    serializer = AbandonedCartSerializer(abandoned_carts, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def track_utm_parameters(request):
    """Track UTM parameters for attribution"""
    serializer = UTMParametersSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Store UTM parameters in session for later use
    utm_data = serializer.validated_data
    for key, value in utm_data.items():
        if value:
            request.session[key] = value
    
    return Response({
        'message': 'UTM parameters tracked successfully.',
        'utm_data': utm_data
    })


class TrackingEventListView(generics.ListAPIView):
    """List tracking events (admin only)"""
    
    serializer_class = TrackingEventSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = TrackingEvent.objects.all().select_related('user', 'pixel').order_by('-created_at')
        
        # Filter by event type
        event_type = self.request.query_params.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Filter by pixel
        pixel_id = self.request.query_params.get('pixel_id')
        if pixel_id:
            queryset = queryset.filter(pixel_id=pixel_id)
        
        # Filter by date range
        days = self.request.query_params.get('days')
        if days:
            start_date = timezone.now() - timedelta(days=int(days))
            queryset = queryset.filter(created_at__gte=start_date)
        
        return queryset
