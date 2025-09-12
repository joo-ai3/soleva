from rest_framework import serializers
from django.contrib.auth import get_user_model
from phonenumber_field.serializerfields import PhoneNumberField
from .models import Address

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    
    phone_number = PhoneNumberField(required=False, allow_blank=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone_number', 'date_of_birth', 'gender', 'language_preference',
            'email_notifications', 'sms_notifications', 'push_notifications',
            'is_verified', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'email', 'username', 'is_verified', 'date_joined', 'last_login']
    
    def validate_phone_number(self, value):
        """Validate phone number uniqueness (excluding current user)"""
        if value:
            user = self.instance
            if User.objects.filter(phone_number=value).exclude(id=user.id if user else None).exists():
                raise serializers.ValidationError("A user with this phone number already exists.")
        return value


class AddressSerializer(serializers.ModelSerializer):
    """Address serializer"""
    
    phone_number = PhoneNumberField()
    full_address = serializers.CharField(read_only=True)
    
    class Meta:
        model = Address
        fields = [
            'id', 'full_name', 'phone_number', 'governorate', 'city', 'area',
            'street_address', 'building_number', 'apartment_number', 'floor_number',
            'landmark', 'postal_code', 'address_type', 'is_default', 'is_active',
            'latitude', 'longitude', 'full_address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Custom validation"""
        user = self.context['request'].user
        
        # If this is set as default, ensure user doesn't already have a default address
        if attrs.get('is_default', False):
            existing_default = Address.objects.filter(user=user, is_default=True)
            if self.instance:
                existing_default = existing_default.exclude(id=self.instance.id)
            
            if existing_default.exists():
                # We'll handle this in the model's save method, but we could warn here
                pass
        
        return attrs
    
    def create(self, validated_data):
        """Create address for current user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserStatsSerializer(serializers.Serializer):
    """User statistics serializer"""
    
    total_orders = serializers.IntegerField(read_only=True)
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    favorite_category = serializers.CharField(read_only=True)
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    last_order_date = serializers.DateTimeField(read_only=True)
    wishlist_items = serializers.IntegerField(read_only=True)


class UserPreferencesSerializer(serializers.ModelSerializer):
    """User preferences serializer"""
    
    class Meta:
        model = User
        fields = [
            'language_preference', 'email_notifications', 
            'sms_notifications', 'push_notifications'
        ]


class UserDashboardSerializer(serializers.Serializer):
    """User dashboard data serializer"""
    
    profile = UserProfileSerializer(read_only=True)
    stats = UserStatsSerializer(read_only=True)
    recent_orders = serializers.ListField(read_only=True)
    addresses_count = serializers.IntegerField(read_only=True)
    default_address = AddressSerializer(read_only=True)


class BulkAddressUpdateSerializer(serializers.Serializer):
    """Bulk address update serializer"""
    
    addresses = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate_addresses(self, value):
        """Validate addresses data"""
        user = self.context['request'].user
        
        # Validate each address
        for addr_data in value:
            if 'id' not in addr_data:
                raise serializers.ValidationError("Each address must have an 'id' field.")
            
            try:
                address = Address.objects.get(id=addr_data['id'], user=user)
            except Address.DoesNotExist:
                raise serializers.ValidationError(f"Address with id {addr_data['id']} not found.")
        
        return value
