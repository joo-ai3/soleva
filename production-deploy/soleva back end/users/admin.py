from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Address, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin"""
    
    list_display = [
        'email', 'username', 'first_name', 'last_name', 
        'is_verified', 'is_active', 'is_staff', 'date_joined'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 'is_verified',
        'language_preference', 'date_joined', 'last_login'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone_number']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 
                      'date_of_birth', 'gender')
        }),
        (_('Preferences'), {
            'fields': ('language_preference', 'email_notifications', 
                      'sms_notifications', 'push_notifications')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions'),
        }),
        (_('Verification'), {
            'fields': ('is_verified', 'verification_code', 'verification_code_expires')
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Address admin"""
    
    list_display = [
        'full_name', 'user', 'governorate', 'city', 
        'address_type', 'is_default', 'is_active', 'created_at'
    ]
    list_filter = [
        'governorate', 'address_type', 'is_default', 
        'is_active', 'created_at'
    ]
    search_fields = [
        'full_name', 'user__email', 'user__first_name', 'user__last_name',
        'governorate', 'city', 'street_address'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Contact Information'), {
            'fields': ('user', 'full_name', 'phone_number')
        }),
        (_('Address Details'), {
            'fields': ('governorate', 'city', 'area', 'street_address',
                      'building_number', 'apartment_number', 'floor_number',
                      'landmark', 'postal_code')
        }),
        (_('Settings'), {
            'fields': ('address_type', 'is_default', 'is_active')
        }),
        (_('Coordinates'), {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """User session admin"""
    
    list_display = [
        'user', 'ip_address', 'country', 'city', 
        'is_active', 'last_activity', 'created_at'
    ]
    list_filter = [
        'is_active', 'country', 'created_at', 'last_activity'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'ip_address', 'session_key'
    ]
    ordering = ['-last_activity']
    
    readonly_fields = ['created_at', 'last_activity']
    
    fieldsets = (
        (_('Session Info'), {
            'fields': ('user', 'session_key', 'is_active')
        }),
        (_('Device Info'), {
            'fields': ('device_info', 'user_agent')
        }),
        (_('Location'), {
            'fields': ('ip_address', 'country', 'city')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'last_activity', 'expires_at')
        }),
    )
