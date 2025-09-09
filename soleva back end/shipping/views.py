from rest_framework import status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.db.models import Q, Avg
from django.db import models
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import Governorate, City, ShippingMethod, ShippingZone, ShippingRate
from .serializers import (
    GovernorateSerializer, CitySerializer, ShippingMethodSerializer,
    ShippingCalculationSerializer, ShippingOptionSerializer,
    AddressValidationSerializer, DeliveryEstimateSerializer,
    DeliveryEstimateResponseSerializer
)


class GovernorateViewSet(ReadOnlyModelViewSet):
    """Governorate viewset"""
    
    serializer_class = GovernorateSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['display_order', 'name_en']
    ordering = ['display_order', 'name_en']
    search_fields = ['name_en', 'name_ar', 'code']
    
    def get_queryset(self):
        """Get active governorates"""
        return Governorate.objects.filter(is_active=True).prefetch_related(
            'cities'
        )
    
    def list(self, request, *args, **kwargs):
        """Get governorates list with caching"""
        cache_key = 'governorates_list'
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            cached_data = serializer.data
            
            # Cache for 1 hour
            cache.set(cache_key, cached_data, 3600)
        
        return Response(cached_data)


class CityViewSet(ReadOnlyModelViewSet):
    """City viewset"""
    
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['display_order', 'name_en', 'estimated_delivery_days']
    ordering = ['display_order', 'name_en']
    search_fields = ['name_en', 'name_ar']
    
    def get_queryset(self):
        """Get active cities"""
        queryset = City.objects.filter(is_active=True).select_related('governorate')
        
        # Filter by governorate if provided
        governorate_id = self.request.query_params.get('governorate_id')
        if governorate_id:
            queryset = queryset.filter(governorate_id=governorate_id)
        
        return queryset


class ShippingMethodViewSet(ReadOnlyModelViewSet):
    """Shipping method viewset"""
    
    serializer_class = ShippingMethodSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['display_order', 'name_en', 'base_cost']
    ordering = ['display_order', 'name_en']
    
    def get_queryset(self):
        """Get active shipping methods"""
        return ShippingMethod.objects.filter(is_active=True)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def calculate_shipping(request):
    """Calculate shipping costs and options"""
    serializer = ShippingCalculationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    governorate_id = data['governorate_id']
    city_id = data.get('city_id')
    total_weight = data['total_weight']
    order_total = data['order_total']
    
    try:
        governorate = Governorate.objects.get(id=governorate_id, is_active=True)
        city = None
        if city_id:
            city = City.objects.get(id=city_id, is_active=True, governorate=governorate)
    except (Governorate.DoesNotExist, City.DoesNotExist):
        return Response({
            'error': 'Invalid location.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get available shipping methods
    shipping_methods = ShippingMethod.objects.filter(is_active=True)
    shipping_options = []
    
    for method in shipping_methods:
        # Check weight restrictions
        if method.max_weight and total_weight > method.max_weight:
            continue
        
        # Calculate cost
        cost = method.calculate_cost(total_weight, order_total)
        
        # Add governorate base cost
        cost += governorate.base_shipping_cost
        
        # Add city additional cost if applicable
        if city:
            cost += city.additional_shipping_cost
        
        # Check if free shipping applies
        is_free = (
            method.free_shipping_threshold and 
            order_total >= method.free_shipping_threshold
        )
        
        if is_free:
            cost = Decimal('0.00')
        
        # Estimate delivery days
        base_days = method.min_delivery_days
        max_days = method.max_delivery_days
        
        if city:
            # Add city-specific delivery time
            base_days += city.estimated_delivery_days
            max_days += city.estimated_delivery_days
        
        shipping_options.append({
            'method_id': method.id,
            'method_name': method.name_en,
            'method_code': method.code,
            'description': method.description_en,
            'cost': cost,
            'estimated_days_min': base_days,
            'estimated_days_max': max_days,
            'is_free': is_free,
            'free_shipping_threshold': method.free_shipping_threshold,
        })
    
    # Sort by cost
    shipping_options.sort(key=lambda x: x['cost'])
    
    response_data = {
        'location': {
            'governorate': governorate.name_en,
            'city': city.name_en if city else None,
        },
        'shipping_options': shipping_options,
        'total_weight': total_weight,
        'order_total': order_total,
    }
    
    return Response(response_data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def validate_address(request):
    """Validate shipping address"""
    serializer = AddressValidationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    governorate = serializer.validated_data['governorate_obj']
    city = serializer.validated_data['city_obj']
    
    return Response({
        'valid': True,
        'governorate': {
            'id': governorate.id,
            'name_en': governorate.name_en,
            'name_ar': governorate.name_ar,
            'code': governorate.code,
        },
        'city': {
            'id': city.id,
            'name_en': city.name_en,
            'name_ar': city.name_ar,
            'estimated_delivery_days': city.estimated_delivery_days,
        },
        'shipping_cost_estimate': governorate.base_shipping_cost + city.additional_shipping_cost,
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def estimate_delivery(request):
    """Estimate delivery date"""
    serializer = DeliveryEstimateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    governorate_id = data['governorate_id']
    city_id = data.get('city_id')
    method_id = data.get('shipping_method_id')
    
    try:
        governorate = Governorate.objects.get(id=governorate_id, is_active=True)
        city = None
        if city_id:
            city = City.objects.get(id=city_id, is_active=True)
        
        method = None
        if method_id:
            method = ShippingMethod.objects.get(id=method_id, is_active=True)
    except (Governorate.DoesNotExist, City.DoesNotExist, ShippingMethod.DoesNotExist):
        return Response({
            'error': 'Invalid parameters.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate delivery estimate
    base_days = 2  # Default processing time
    max_days = 3
    
    if method:
        base_days = method.min_delivery_days
        max_days = method.max_delivery_days
    
    if city:
        base_days += city.estimated_delivery_days
        max_days += city.estimated_delivery_days
    
    # Calculate estimated date (excluding weekends)
    estimated_date = timezone.now().date()
    days_added = 0
    
    while days_added < base_days:
        estimated_date += timedelta(days=1)
        # Skip weekends (Friday and Saturday in Egypt)
        if estimated_date.weekday() not in [4, 5]:  # 4=Friday, 5=Saturday
            days_added += 1
    
    note = "Delivery estimate excludes weekends and public holidays."
    if governorate.name_en not in ['Cairo', 'Giza', 'Alexandria']:
        note += " Remote areas may require additional time."
    
    response_data = {
        'estimated_date': estimated_date,
        'min_days': base_days,
        'max_days': max_days,
        'business_days': True,
        'note': note,
    }
    
    serializer = DeliveryEstimateResponseSerializer(response_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_locations(request):
    """Search governorates and cities"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return Response([])
    
    # Search governorates
    governorates = Governorate.objects.filter(
        Q(name_en__icontains=query) | Q(name_ar__icontains=query),
        is_active=True
    ).values('id', 'name_en', 'name_ar', 'code')[:5]
    
    # Search cities
    cities = City.objects.filter(
        Q(name_en__icontains=query) | Q(name_ar__icontains=query),
        is_active=True
    ).select_related('governorate').values(
        'id', 'name_en', 'name_ar', 
        'governorate__id', 'governorate__name_en', 'governorate__name_ar'
    )[:10]
    
    results = {
        'governorates': list(governorates),
        'cities': [
            {
                'id': city['id'],
                'name_en': city['name_en'],
                'name_ar': city['name_ar'],
                'governorate': {
                    'id': city['governorate__id'],
                    'name_en': city['governorate__name_en'],
                    'name_ar': city['governorate__name_ar'],
                }
            }
            for city in cities
        ]
    }
    
    return Response(results)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def shipping_zones(request):
    """Get shipping zones information"""
    cache_key = 'shipping_zones'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        zones = ShippingZone.objects.filter(is_active=True).prefetch_related(
            'governorates'
        )
        
        zones_data = []
        for zone in zones:
            zone_data = {
                'id': zone.id,
                'name_en': zone.name_en,
                'name_ar': zone.name_ar,
                'description': zone.description,
                'governorates': [
                    {
                        'id': gov.id,
                        'name_en': gov.name_en,
                        'name_ar': gov.name_ar,
                        'base_shipping_cost': gov.base_shipping_cost,
                    }
                    for gov in zone.governorates.filter(is_active=True)
                ]
            }
            zones_data.append(zone_data)
        
        cached_data = zones_data
        # Cache for 2 hours
        cache.set(cache_key, cached_data, 7200)
    
    return Response(cached_data)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def shipping_stats(request):
    """Get shipping statistics (admin only)"""
    stats = {
        'total_governorates': Governorate.objects.filter(is_active=True).count(),
        'total_cities': City.objects.filter(is_active=True).count(),
        'shipping_methods': ShippingMethod.objects.filter(is_active=True).count(),
        'shipping_zones': ShippingZone.objects.filter(is_active=True).count(),
        
        # Coverage stats
        'covered_governorates': Governorate.objects.filter(
            is_active=True,
            cities__is_active=True
        ).distinct().count(),
        
        'average_shipping_cost': Governorate.objects.filter(
            is_active=True
        ).aggregate(
            avg_cost=Avg('base_shipping_cost')
        )['avg_cost'],
    }
    
    return Response(stats)
