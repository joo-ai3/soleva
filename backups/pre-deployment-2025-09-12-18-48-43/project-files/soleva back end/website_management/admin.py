from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import WebsiteSection, SiteConfiguration, NotificationBanner, UserMessage


@admin.register(WebsiteSection)
class WebsiteSectionAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'section_type', 'is_active', 'display_order', 
        'image_preview', 'updated_at'
    ]
    list_filter = ['section_type', 'is_active', 'created_at']
    search_fields = ['name', 'title_en', 'title_ar', 'content_en', 'content_ar']
    ordering = ['display_order', 'created_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'section_type', 'is_active', 'display_order')
        }),
        (_('Content'), {
            'fields': (
                'title_en', 'title_ar',
                'subtitle_en', 'subtitle_ar',
                'content_en', 'content_ar'
            )
        }),
        (_('Media'), {
            'fields': ('image', 'background_image', 'video_url'),
            'classes': ('collapse',)
        }),
        (_('Call to Action'), {
            'fields': ('cta_text_en', 'cta_text_ar', 'cta_url'),
            'classes': ('collapse',)
        }),
        (_('Styling'), {
            'fields': ('background_color', 'text_color', 'custom_css'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return _('No image')
    image_preview.short_description = _('Preview')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one configuration instance
        return not SiteConfiguration.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of site configuration
        return False
    
    fieldsets = (
        (_('Site Information'), {
            'fields': (
                'site_name_en', 'site_name_ar',
                'site_description_en', 'site_description_ar'
            )
        }),
        (_('Contact Information'), {
            'fields': (
                'primary_email', 'support_email', 'sales_email', 'business_email',
                'phone_number', 'whatsapp_number',
                'address_en', 'address_ar'
            )
        }),
        (_('Social Media'), {
            'fields': (
                'facebook_url', 'instagram_url', 'twitter_url',
                'youtube_url', 'tiktok_url'
            )
        }),
        (_('SEO Settings'), {
            'fields': (
                'meta_keywords_en', 'meta_keywords_ar',
                'google_analytics_id', 'facebook_pixel_id'
            ),
            'classes': ('collapse',)
        }),
        (_('Business Information'), {
            'fields': (
                'business_hours',
                'shipping_info_en', 'shipping_info_ar',
                'return_policy_en', 'return_policy_ar'
            ),
            'classes': ('collapse',)
        }),
        (_('Maintenance Mode'), {
            'fields': (
                'maintenance_mode',
                'maintenance_message_en', 'maintenance_message_ar'
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificationBanner)
class NotificationBannerAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'banner_type', 'display_location', 'is_active',
        'priority', 'scheduled_status', 'created_at'
    ]
    list_filter = [
        'banner_type', 'display_location', 'is_active', 
        'is_dismissible', 'created_at'
    ]
    search_fields = ['title', 'message_en', 'message_ar']
    ordering = ['-priority', 'display_order', '-created_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'banner_type', 'display_location')
        }),
        (_('Message Content'), {
            'fields': ('message_en', 'message_ar')
        }),
        (_('Display Settings'), {
            'fields': (
                'is_active', 'is_dismissible', 'auto_hide_after',
                'priority', 'display_order'
            )
        }),
        (_('Scheduling'), {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',)
        }),
        (_('Styling'), {
            'fields': ('background_color', 'text_color', 'icon'),
            'classes': ('collapse',)
        }),
        (_('Call to Action'), {
            'fields': ('cta_text_en', 'cta_text_ar', 'cta_url'),
            'classes': ('collapse',)
        }),
    )
    
    def scheduled_status(self, obj):
        if obj.should_display:
            return format_html(
                '<span style="color: green; font-weight: bold;">●</span> {}',
                _('Active')
            )
        elif obj.is_active and not obj.is_scheduled_active:
            return format_html(
                '<span style="color: orange; font-weight: bold;">●</span> {}',
                _('Scheduled')
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">●</span> {}',
                _('Inactive')
            )
    scheduled_status.short_description = _('Status')


@admin.register(UserMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = [
        'subject_en', 'user', 'message_type', 'is_read', 
        'is_important', 'sent_at'
    ]
    list_filter = [
        'message_type', 'is_read', 'is_important', 'sent_at'
    ]
    search_fields = [
        'subject_en', 'subject_ar', 'message_en', 'message_ar',
        'user__email', 'user__first_name', 'user__last_name'
    ]
    ordering = ['-is_important', '-sent_at']
    
    fieldsets = (
        (_('Recipient'), {
            'fields': ('user',)
        }),
        (_('Message Content'), {
            'fields': (
                'subject_en', 'subject_ar',
                'message_en', 'message_ar',
                'message_type'
            )
        }),
        (_('Status'), {
            'fields': ('is_read', 'is_important')
        }),
        (_('Attachments & Actions'), {
            'fields': (
                'attachment', 'action_url',
                'action_text_en', 'action_text_ar'
            ),
            'classes': ('collapse',)
        }),
        (_('Related Objects'), {
            'fields': ('related_order', 'related_product'),
            'classes': ('collapse',)
        }),
        (_('Scheduling'), {
            'fields': ('expires_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['sent_at', 'read_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'related_order', 'related_product')


# Custom admin site customization
admin.site.site_header = _('Soleva Admin Panel')
admin.site.site_title = _('Soleva Admin')
admin.site.index_title = _('Website Management Dashboard')
