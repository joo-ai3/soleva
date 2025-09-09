from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

from .models import WebsiteSection, SiteConfiguration, NotificationBanner, UserMessage
from .serializers import (
    WebsiteSectionSerializer, SiteConfigurationSerializer, 
    NotificationBannerSerializer, UserMessageSerializer, UserMessageCreateSerializer,
    WebsiteSectionPublicSerializer, SiteConfigurationPublicSerializer, 
    NotificationBannerPublicSerializer
)

User = get_user_model()


# Admin Views (require admin permissions)
class WebsiteSectionListCreateView(generics.ListCreateAPIView):
    """Admin view for listing and creating website sections"""
    queryset = WebsiteSection.objects.all()
    serializer_class = WebsiteSectionSerializer
    permission_classes = [permissions.IsAdminUser]
    ordering = ['display_order', 'created_at']


class WebsiteSectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin view for retrieving, updating, and deleting website sections"""
    queryset = WebsiteSection.objects.all()
    serializer_class = WebsiteSectionSerializer
    permission_classes = [permissions.IsAdminUser]


class SiteConfigurationView(generics.RetrieveUpdateAPIView):
    """Admin view for site configuration"""
    serializer_class = SiteConfigurationSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_object(self):
        config, created = SiteConfiguration.objects.get_or_create()
        return config


class NotificationBannerListCreateView(generics.ListCreateAPIView):
    """Admin view for listing and creating notification banners"""
    queryset = NotificationBanner.objects.all()
    serializer_class = NotificationBannerSerializer
    permission_classes = [permissions.IsAdminUser]
    ordering = ['-priority', 'display_order', '-created_at']


class NotificationBannerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin view for retrieving, updating, and deleting notification banners"""
    queryset = NotificationBanner.objects.all()
    serializer_class = NotificationBannerSerializer
    permission_classes = [permissions.IsAdminUser]


class UserMessageListView(generics.ListAPIView):
    """Admin view for listing user messages"""
    serializer_class = UserMessageSerializer
    permission_classes = [permissions.IsAdminUser]
    ordering = ['-is_important', '-sent_at']
    
    def get_queryset(self):
        queryset = UserMessage.objects.select_related('user', 'related_order', 'related_product')
        
        # Filter by user email if provided
        user_email = self.request.query_params.get('user_email')
        if user_email:
            queryset = queryset.filter(user__email__icontains=user_email)
        
        # Filter by message type if provided
        message_type = self.request.query_params.get('message_type')
        if message_type:
            queryset = queryset.filter(message_type=message_type)
        
        # Filter by read status if provided
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        return queryset


class UserMessageCreateView(generics.CreateAPIView):
    """Admin view for creating user messages"""
    serializer_class = UserMessageCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class UserMessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin view for retrieving, updating, and deleting user messages"""
    queryset = UserMessage.objects.all()
    serializer_class = UserMessageSerializer
    permission_classes = [permissions.IsAdminUser]


# Public Views (for frontend)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def website_sections_public(request):
    """Public endpoint to get active website sections"""
    section_type = request.GET.get('section_type')
    
    queryset = WebsiteSection.objects.filter(is_active=True).order_by('display_order', 'created_at')
    
    if section_type:
        queryset = queryset.filter(section_type=section_type)
    
    serializer = WebsiteSectionPublicSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def site_configuration_public(request):
    """Public endpoint to get site configuration"""
    config, created = SiteConfiguration.objects.get_or_create()
    serializer = SiteConfigurationPublicSerializer(config)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def notification_banners_public(request):
    """Public endpoint to get active notification banners"""
    location = request.GET.get('location', 'all_pages')
    
    now = timezone.now()
    queryset = NotificationBanner.objects.filter(
        is_active=True,
        display_location__in=[location, 'all_pages']
    ).filter(
        Q(start_date__isnull=True) | Q(start_date__lte=now)
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=now)
    ).order_by('-priority', 'display_order')
    
    serializer = NotificationBannerPublicSerializer(queryset, many=True)
    return Response(serializer.data)


# User Views (require authentication)
class UserMessagesView(generics.ListAPIView):
    """User view for their own messages"""
    serializer_class = UserMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-is_important', '-sent_at']
    
    def get_queryset(self):
        now = timezone.now()
        return UserMessage.objects.filter(
            user=self.request.user
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gte=now)
        ).select_related('related_order', 'related_product')


class UserMessageDetailView(generics.RetrieveAPIView):
    """User view for retrieving a specific message"""
    serializer_class = UserMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserMessage.objects.filter(user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Mark message as read when retrieved
        if not instance.is_read:
            instance.mark_as_read()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_message_as_read(request, message_id):
    """Mark a user message as read"""
    message = get_object_or_404(UserMessage, id=message_id, user=request.user)
    message.mark_as_read()
    return Response({'status': 'success', 'message': 'Message marked as read'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_messages_count(request):
    """Get count of unread messages for the authenticated user"""
    count = UserMessage.objects.filter(
        user=request.user,
        is_read=False
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gte=timezone.now())
    ).count()
    
    return Response({'unread_count': count})


# Utility Views
@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def bulk_send_message(request):
    """Bulk send messages to users based on criteria"""
    data = request.data
    
    # Get message content
    message_data = {
        'subject_en': data.get('subject_en'),
        'subject_ar': data.get('subject_ar'),
        'message_en': data.get('message_en'),
        'message_ar': data.get('message_ar'),
        'message_type': data.get('message_type', 'announcement'),
        'is_important': data.get('is_important', False),
        'action_url': data.get('action_url'),
        'action_text_en': data.get('action_text_en'),
        'action_text_ar': data.get('action_text_ar'),
        'expires_at': data.get('expires_at'),
    }
    
    # Get target users based on criteria
    target_criteria = data.get('target_criteria', {})
    users_queryset = User.objects.filter(is_active=True)
    
    # Filter by user type
    if target_criteria.get('user_type') == 'customers':
        users_queryset = users_queryset.filter(is_staff=False, is_superuser=False)
    elif target_criteria.get('user_type') == 'staff':
        users_queryset = users_queryset.filter(is_staff=True)
    
    # Filter by registration date
    if target_criteria.get('registered_after'):
        users_queryset = users_queryset.filter(date_joined__gte=target_criteria['registered_after'])
    
    if target_criteria.get('registered_before'):
        users_queryset = users_queryset.filter(date_joined__lte=target_criteria['registered_before'])
    
    # Filter by last login
    if target_criteria.get('last_login_after'):
        users_queryset = users_queryset.filter(last_login__gte=target_criteria['last_login_after'])
    
    # Create messages
    messages_created = 0
    for user in users_queryset:
        message_data['user'] = user
        UserMessage.objects.create(**message_data)
        messages_created += 1
    
    return Response({
        'status': 'success',
        'messages_sent': messages_created,
        'message': f'Successfully sent message to {messages_created} users'
    })
