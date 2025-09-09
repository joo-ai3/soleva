from rest_framework import status, permissions, generics, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend

from .models import Address
from .serializers import (
    UserProfileSerializer,
    AddressSerializer,
    UserStatsSerializer,
    UserPreferencesSerializer,
    UserDashboardSerializer,
    BulkAddressUpdateSerializer
)

User = get_user_model()


class UserProfileView(APIView):
    """User profile management"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user profile"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Update user profile"""
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully.',
                'user': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        """Partially update user profile"""
        return self.put(request)


class AddressViewSet(ModelViewSet):
    """Address management viewset"""
    
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['address_type', 'is_default', 'is_active', 'governorate', 'city']
    ordering_fields = ['created_at', 'is_default']
    ordering = ['-is_default', '-created_at']
    
    def get_queryset(self):
        """Get addresses for current user"""
        return Address.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        """Create address for current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set address as default"""
        address = self.get_object()
        
        # Remove default from other addresses
        Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Set this address as default
        address.is_default = True
        address.save()
        
        return Response({
            'message': 'Default address updated successfully.',
            'address': AddressSerializer(address).data
        })
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update addresses"""
        serializer = BulkAddressUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            addresses_data = serializer.validated_data['addresses']
            updated_addresses = []
            
            for addr_data in addresses_data:
                address_id = addr_data.pop('id')
                address = Address.objects.get(id=address_id, user=request.user)
                
                # Update address fields
                for field, value in addr_data.items():
                    setattr(address, field, value)
                
                address.save()
                updated_addresses.append(AddressSerializer(address).data)
            
            return Response({
                'message': f'Successfully updated {len(updated_addresses)} addresses.',
                'addresses': updated_addresses
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserStatsView(APIView):
    """User statistics view"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user statistics"""
        user = request.user
        
        # Get order statistics (you'll need to import Order model when it's ready)
        # from orders.models import Order
        # orders = Order.objects.filter(user=user)
        
        # For now, return mock data
        stats = {
            'total_orders': 0,  # orders.count()
            'total_spent': 0.00,  # orders.aggregate(total=Sum('total_amount'))['total'] or 0
            'favorite_category': 'Fashion',  # Most ordered category
            'average_order_value': 0.00,  # orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
            'last_order_date': None,  # orders.order_by('-created_at').first().created_at if orders.exists() else None
            'wishlist_items': 0,  # user.saved_items.count()
        }
        
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)


class UserDashboardView(APIView):
    """User dashboard view"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user dashboard data"""
        user = request.user
        
        # Get user profile
        profile_data = UserProfileSerializer(user).data
        
        # Get user stats
        stats_view = UserStatsView()
        stats_data = stats_view.get(request).data
        
        # Get recent orders (mock for now)
        recent_orders = []  # Implement when Order model is ready
        
        # Get addresses count
        addresses_count = user.addresses.filter(is_active=True).count()
        
        # Get default address
        default_address = user.addresses.filter(is_default=True, is_active=True).first()
        default_address_data = AddressSerializer(default_address).data if default_address else None
        
        dashboard_data = {
            'profile': profile_data,
            'stats': stats_data,
            'recent_orders': recent_orders,
            'addresses_count': addresses_count,
            'default_address': default_address_data,
        }
        
        return Response(dashboard_data)


class UserPreferencesView(APIView):
    """User preferences management"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user preferences"""
        serializer = UserPreferencesSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Update user preferences"""
        serializer = UserPreferencesSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Preferences updated successfully.',
                'preferences': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_account(request):
    """Delete user account"""
    user = request.user
    
    # You might want to add additional verification here
    # like password confirmation or email verification
    
    # Soft delete - deactivate account
    user.is_active = False
    user.email = f"deleted_{user.id}_{user.email}"
    user.username = f"deleted_{user.id}_{user.username}"
    user.save()
    
    return Response({
        'message': 'Account deleted successfully.'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def export_user_data(request):
    """Export user data (GDPR compliance)"""
    user = request.user
    
    # Collect all user data
    user_data = {
        'profile': UserProfileSerializer(user).data,
        'addresses': AddressSerializer(user.addresses.filter(is_active=True), many=True).data,
        # Add more data as needed (orders, reviews, etc.)
    }
    
    # In a real implementation, you'd probably:
    # 1. Generate a file (JSON, CSV, etc.)
    # 2. Store it temporarily
    # 3. Send download link via email
    # 4. Clean up file after download
    
    return Response({
        'message': 'Data export initiated. You will receive a download link via email.',
        'data': user_data  # For demo purposes, returning data directly
    })


class UserSearchView(generics.ListAPIView):
    """Search users (admin only)"""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]  # Add admin permission when ready
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering_fields = ['date_joined', 'last_login', 'email']
    ordering = ['-date_joined']
    filterset_fields = ['is_active', 'is_verified', 'language_preference']
    
    def get_queryset(self):
        """Get users queryset"""
        # For now, return all users. In production, add proper admin permissions
        return User.objects.all()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_activity(request):
    """Get user activity summary"""
    user = request.user
    
    # Calculate activity metrics
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    last_7_days = now - timedelta(days=7)
    
    activity = {
        'last_login': user.last_login,
        'account_age_days': (now - user.date_joined).days,
        'is_active_user': user.last_login and user.last_login > last_30_days,
        'addresses_count': user.addresses.filter(is_active=True).count(),
        # Add more activity metrics as needed
    }
    
    return Response(activity)
