from rest_framework import serializers
from .models import WebsiteSection, SiteConfiguration, NotificationBanner, UserMessage


class WebsiteSectionSerializer(serializers.ModelSerializer):
    """Serializer for website sections"""
    
    class Meta:
        model = WebsiteSection
        fields = [
            'id', 'name', 'section_type', 'title_en', 'title_ar',
            'subtitle_en', 'subtitle_ar', 'content_en', 'content_ar',
            'image', 'background_image', 'video_url',
            'cta_text_en', 'cta_text_ar', 'cta_url',
            'is_active', 'display_order',
            'background_color', 'text_color', 'custom_css',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SiteConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for site configuration"""
    
    class Meta:
        model = SiteConfiguration
        fields = [
            'site_name_en', 'site_name_ar',
            'site_description_en', 'site_description_ar',
            'primary_email', 'support_email', 'sales_email', 'business_email',
            'phone_number', 'whatsapp_number',
            'address_en', 'address_ar',
            'facebook_url', 'instagram_url', 'twitter_url', 'youtube_url', 'tiktok_url',
            'meta_keywords_en', 'meta_keywords_ar',
            'google_analytics_id', 'facebook_pixel_id',
            'business_hours',
            'shipping_info_en', 'shipping_info_ar',
            'return_policy_en', 'return_policy_ar',
            'maintenance_mode', 'maintenance_message_en', 'maintenance_message_ar',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class NotificationBannerSerializer(serializers.ModelSerializer):
    """Serializer for notification banners"""
    
    should_display = serializers.ReadOnlyField()
    is_scheduled_active = serializers.ReadOnlyField()
    
    class Meta:
        model = NotificationBanner
        fields = [
            'id', 'title', 'message_en', 'message_ar',
            'banner_type', 'display_location',
            'is_active', 'is_dismissible', 'auto_hide_after',
            'start_date', 'end_date',
            'background_color', 'text_color', 'icon',
            'cta_text_en', 'cta_text_ar', 'cta_url',
            'priority', 'display_order',
            'should_display', 'is_scheduled_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'should_display', 'is_scheduled_active', 'created_at', 'updated_at']


class UserMessageSerializer(serializers.ModelSerializer):
    """Serializer for user messages"""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserMessage
        fields = [
            'id', 'user', 'user_email', 'user_name',
            'subject_en', 'subject_ar', 'message_en', 'message_ar',
            'message_type', 'is_read', 'is_important',
            'attachment', 'action_url', 'action_text_en', 'action_text_ar',
            'related_order', 'related_product',
            'sent_at', 'read_at', 'expires_at'
        ]
        read_only_fields = ['id', 'user_email', 'user_name', 'sent_at', 'read_at']


class UserMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating user messages"""
    
    # Allow sending to multiple users
    user_emails = serializers.ListField(
        child=serializers.EmailField(),
        write_only=True,
        required=False,
        help_text="List of user emails to send the message to"
    )
    send_to_all_users = serializers.BooleanField(
        write_only=True,
        default=False,
        help_text="Send message to all active users"
    )
    
    class Meta:
        model = UserMessage
        fields = [
            'subject_en', 'subject_ar', 'message_en', 'message_ar',
            'message_type', 'is_important',
            'attachment', 'action_url', 'action_text_en', 'action_text_ar',
            'expires_at',
            'user_emails', 'send_to_all_users'
        ]
    
    def create(self, validated_data):
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user_emails = validated_data.pop('user_emails', [])
        send_to_all_users = validated_data.pop('send_to_all_users', False)
        
        messages = []
        
        if send_to_all_users:
            # Send to all active users
            users = User.objects.filter(is_active=True)
        elif user_emails:
            # Send to specific users
            users = User.objects.filter(email__in=user_emails, is_active=True)
        else:
            raise serializers.ValidationError("Either provide user_emails or set send_to_all_users to True")
        
        for user in users:
            message_data = validated_data.copy()
            message_data['user'] = user
            message = UserMessage.objects.create(**message_data)
            messages.append(message)
        
        return messages[0] if messages else None  # Return first message for response


class WebsiteSectionPublicSerializer(serializers.ModelSerializer):
    """Public serializer for website sections (for frontend)"""
    
    class Meta:
        model = WebsiteSection
        fields = [
            'id', 'name', 'section_type',
            'title_en', 'title_ar', 'subtitle_en', 'subtitle_ar',
            'content_en', 'content_ar',
            'image', 'background_image', 'video_url',
            'cta_text_en', 'cta_text_ar', 'cta_url',
            'display_order', 'background_color', 'text_color'
        ]


class SiteConfigurationPublicSerializer(serializers.ModelSerializer):
    """Public serializer for site configuration (for frontend)"""
    
    class Meta:
        model = SiteConfiguration
        fields = [
            'site_name_en', 'site_name_ar',
            'site_description_en', 'site_description_ar',
            'primary_email', 'support_email', 'sales_email', 'business_email',
            'phone_number', 'whatsapp_number',
            'address_en', 'address_ar',
            'facebook_url', 'instagram_url', 'twitter_url', 'youtube_url', 'tiktok_url',
            'business_hours',
            'shipping_info_en', 'shipping_info_ar',
            'return_policy_en', 'return_policy_ar'
        ]


class NotificationBannerPublicSerializer(serializers.ModelSerializer):
    """Public serializer for notification banners (for frontend)"""
    
    class Meta:
        model = NotificationBanner
        fields = [
            'id', 'title', 'message_en', 'message_ar',
            'banner_type', 'display_location',
            'is_dismissible', 'auto_hide_after',
            'background_color', 'text_color', 'icon',
            'cta_text_en', 'cta_text_ar', 'cta_url',
            'priority'
        ]
