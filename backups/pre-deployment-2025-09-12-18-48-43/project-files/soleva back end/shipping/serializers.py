from rest_framework import serializers
from .models import Governorate, City, ShippingMethod, ShippingZone, ShippingRate


class CitySerializer(serializers.ModelSerializer):
    """City serializer"""
    
    governorate_name = serializers.CharField(source='governorate.name_en', read_only=True)
    total_shipping_cost = serializers.ReadOnlyField()
    
    class Meta:
        model = City
        fields = [
            'id', 'name_en', 'name_ar', 'governorate', 'governorate_name',
            'latitude', 'longitude', 'is_active', 'additional_shipping_cost',
            'estimated_delivery_days', 'display_order', 'total_shipping_cost'
        ]


class GovernorateSerializer(serializers.ModelSerializer):
    """Governorate serializer"""
    
    cities = CitySerializer(many=True, read_only=True)
    cities_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Governorate
        fields = [
            'id', 'name_en', 'name_ar', 'code', 'latitude', 'longitude',
            'is_active', 'base_shipping_cost', 'display_order',
            'cities', 'cities_count'
        ]
    
    def get_cities_count(self, obj):
        """Get active cities count"""
        return obj.cities.filter(is_active=True).count()


class ShippingMethodSerializer(serializers.ModelSerializer):
    """Shipping method serializer"""
    
    class Meta:
        model = ShippingMethod
        fields = [
            'id', 'name_en', 'name_ar', 'code', 'description_en', 'description_ar',
            'base_cost', 'cost_per_kg', 'free_shipping_threshold',
            'min_delivery_days', 'max_delivery_days', 'max_weight', 'max_dimensions',
            'is_active', 'display_order'
        ]


class ShippingZoneSerializer(serializers.ModelSerializer):
    """Shipping zone serializer"""
    
    governorates = GovernorateSerializer(many=True, read_only=True)
    governorates_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ShippingZone
        fields = [
            'id', 'name_en', 'name_ar', 'description', 'is_active',
            'governorates', 'governorates_count', 'created_at'
        ]
    
    def get_governorates_count(self, obj):
        """Get governorates count"""
        return obj.governorates.count()


class ShippingRateSerializer(serializers.ModelSerializer):
    """Shipping rate serializer"""
    
    zone_name = serializers.CharField(source='zone.name_en', read_only=True)
    method_name = serializers.CharField(source='method.name_en', read_only=True)
    
    class Meta:
        model = ShippingRate
        fields = [
            'id', 'zone', 'zone_name', 'method', 'method_name',
            'base_cost', 'cost_per_kg', 'min_weight', 'max_weight',
            'min_order_value', 'max_order_value', 'is_active'
        ]


class ShippingCalculationSerializer(serializers.Serializer):
    """Shipping calculation request serializer"""
    
    governorate_id = serializers.IntegerField()
    city_id = serializers.IntegerField(required=False, allow_null=True)
    total_weight = serializers.DecimalField(
        max_digits=8, 
        decimal_places=3, 
        required=False, 
        default=0.500  # Default 500g
    )
    order_total = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False, 
        default=0.00
    )
    
    def validate_governorate_id(self, value):
        """Validate governorate exists"""
        try:
            Governorate.objects.get(id=value, is_active=True)
        except Governorate.DoesNotExist:
            raise serializers.ValidationError("Governorate not found.")
        return value
    
    def validate_city_id(self, value):
        """Validate city exists if provided"""
        if value:
            try:
                City.objects.get(id=value, is_active=True)
            except City.DoesNotExist:
                raise serializers.ValidationError("City not found.")
        return value


class ShippingOptionSerializer(serializers.Serializer):
    """Shipping option response serializer"""
    
    method_id = serializers.IntegerField()
    method_name = serializers.CharField()
    method_code = serializers.CharField()
    description = serializers.CharField()
    cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    estimated_days_min = serializers.IntegerField()
    estimated_days_max = serializers.IntegerField()
    is_free = serializers.BooleanField()
    free_shipping_threshold = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        allow_null=True
    )


class AddressValidationSerializer(serializers.Serializer):
    """Address validation serializer"""
    
    governorate = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    
    def validate(self, attrs):
        """Validate address components"""
        governorate_name = attrs['governorate']
        city_name = attrs['city']
        
        # Check if governorate exists
        try:
            governorate = Governorate.objects.get(
                Q(name_en__iexact=governorate_name) | Q(name_ar__iexact=governorate_name),
                is_active=True
            )
        except Governorate.DoesNotExist:
            raise serializers.ValidationError({
                'governorate': f'Governorate "{governorate_name}" not found.'
            })
        
        # Check if city exists in this governorate
        try:
            city = City.objects.get(
                Q(name_en__iexact=city_name) | Q(name_ar__iexact=city_name),
                governorate=governorate,
                is_active=True
            )
        except City.DoesNotExist:
            raise serializers.ValidationError({
                'city': f'City "{city_name}" not found in {governorate.name_en}.'
            })
        
        attrs['governorate_obj'] = governorate
        attrs['city_obj'] = city
        return attrs


class DeliveryEstimateSerializer(serializers.Serializer):
    """Delivery estimate serializer"""
    
    governorate_id = serializers.IntegerField()
    city_id = serializers.IntegerField(required=False, allow_null=True)
    shipping_method_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_governorate_id(self, value):
        """Validate governorate"""
        try:
            Governorate.objects.get(id=value, is_active=True)
        except Governorate.DoesNotExist:
            raise serializers.ValidationError("Governorate not found.")
        return value
    
    def validate_city_id(self, value):
        """Validate city"""
        if value:
            try:
                City.objects.get(id=value, is_active=True)
            except City.DoesNotExist:
                raise serializers.ValidationError("City not found.")
        return value
    
    def validate_shipping_method_id(self, value):
        """Validate shipping method"""
        if value:
            try:
                ShippingMethod.objects.get(id=value, is_active=True)
            except ShippingMethod.DoesNotExist:
                raise serializers.ValidationError("Shipping method not found.")
        return value


class DeliveryEstimateResponseSerializer(serializers.Serializer):
    """Delivery estimate response serializer"""
    
    estimated_date = serializers.DateField()
    min_days = serializers.IntegerField()
    max_days = serializers.IntegerField()
    business_days = serializers.BooleanField()
    note = serializers.CharField()
