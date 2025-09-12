from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import OTPConfiguration, OTPRequest, OTPAttemptLog, SecurityNotification


@admin.register(OTPConfiguration)
class OTPConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code_length', 'expiry_minutes', 'max_attempts', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Settings', {
            'fields': ('name', 'is_active')
        }),
        ('OTP Configuration', {
            'fields': ('code_length', 'expiry_minutes', 'max_attempts')
        }),
        ('Rate Limiting', {
            'fields': ('resend_cooldown_minutes', 'rate_limit_requests', 'rate_limit_window_minutes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp_type', 'code', 'status_display', 'attempts_count', 'created_at', 'expires_at')
    list_filter = ('otp_type', 'is_used', 'is_expired', 'is_invalidated', 'created_at')
    search_fields = ('email', 'code', 'user__username')
    readonly_fields = ('code', 'created_at', 'expires_at', 'used_at', 'status_display')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('email', 'user', 'otp_type', 'code')
        }),
        ('Status', {
            'fields': ('status_display', 'attempts_count', 'is_used', 'is_expired', 'is_invalidated')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at', 'used_at')
        }),
        ('Security Information', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': ('config',),
            'classes': ('collapse',)
        })
    )
    
    def status_display(self, obj):
        if obj.is_used:
            return format_html('<span style="color: green;">✓ Used</span>')
        elif obj.is_expired:
            return format_html('<span style="color: red;">⏰ Expired</span>')
        elif obj.is_invalidated:
            return format_html('<span style="color: red;">❌ Invalidated</span>')
        elif timezone.now() > obj.expires_at:
            return format_html('<span style="color: orange;">⏰ Expired</span>')
        else:
            return format_html('<span style="color: blue;">⏳ Active</span>')
    status_display.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'config')


@admin.register(OTPAttemptLog)
class OTPAttemptLogAdmin(admin.ModelAdmin):
    list_display = ('otp_request_email', 'provided_code', 'is_successful', 'attempted_at', 'ip_address')
    list_filter = ('is_successful', 'attempted_at')
    search_fields = ('otp_request__email', 'provided_code', 'ip_address')
    readonly_fields = ('otp_request', 'provided_code', 'is_successful', 'attempted_at', 'ip_address', 'user_agent')
    date_hierarchy = 'attempted_at'
    
    def otp_request_email(self, obj):
        return obj.otp_request.email
    otp_request_email.short_description = 'Email'
    
    def has_add_permission(self, request):
        return False  # Prevent manual addition
    
    def has_change_permission(self, request, obj=None):
        return False  # Prevent manual changes
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('otp_request')


@admin.register(SecurityNotification)
class SecurityNotificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'notification_type', 'is_sent', 'sent_at', 'created_at')
    list_filter = ('notification_type', 'is_sent', 'created_at')
    search_fields = ('email', 'user__username', 'subject')
    readonly_fields = ('created_at', 'sent_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('user', 'email', 'notification_type', 'subject')
        }),
        ('Content', {
            'fields': ('message',),
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_sent', 'sent_at', 'created_at')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Custom admin site configuration
admin.site.site_header = "Soleva OTP Administration"
admin.site.site_title = "OTP Admin"
admin.site.index_title = "Welcome to OTP Administration"
