from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import FlashSale, SpecialOffer, OfferUsage, FlashSaleProduct


class FlashSaleProductInline(admin.TabularInline):
    model = FlashSaleProduct
    extra = 0
    fields = ['product', 'discount_type', 'discount_value', 'quantity_limit', 'is_featured', 'display_order']
    readonly_fields = ['sold_quantity']


@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):
    list_display = [
        'name_en', 'status_badge', 'start_time', 'end_time', 
        'current_usage_count', 'total_usage_limit', 'display_priority'
    ]
    list_filter = ['is_active', 'start_time', 'end_time']
    search_fields = ['name_en', 'name_ar', 'description_en']
    readonly_fields = ['id', 'current_usage_count', 'created_at', 'updated_at', 'time_remaining_display']
    inlines = [FlashSaleProductInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name_en', 'name_ar', 'description_en', 'description_ar')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'time_remaining_display')
        }),
        ('Display Settings', {
            'fields': ('banner_image', 'banner_color', 'text_color', 'display_priority', 'show_countdown')
        }),
        ('Usage Restrictions', {
            'fields': ('max_uses_per_customer', 'total_usage_limit', 'current_usage_count')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        now = timezone.now()
        if obj.is_running:
            color = 'green'
            status = 'Running'
        elif obj.is_upcoming:
            color = 'orange'
            status = 'Upcoming'
        elif obj.is_expired:
            color = 'red'
            status = 'Expired'
        else:
            color = 'gray'
            status = 'Inactive'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    status_badge.short_description = 'Status'
    
    def time_remaining_display(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        elif obj.is_upcoming:
            delta = obj.start_time - timezone.now()
            return format_html('<span style="color: orange;">Starts in: {}</span>', delta)
        elif obj.is_running:
            delta = obj.end_time - timezone.now()
            return format_html('<span style="color: green;">Ends in: {}</span>', delta)
        else:
            return 'Not active'
    time_remaining_display.short_description = 'Time Remaining'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('products__product')


@admin.register(SpecialOffer)
class SpecialOfferAdmin(admin.ModelAdmin):
    list_display = [
        'name_en', 'offer_type', 'status_badge', 'start_time', 'end_time',
        'current_usage_count', 'total_usage_limit'
    ]
    list_filter = ['is_active', 'offer_type', 'start_time', 'discount_type']
    search_fields = ['name_en', 'name_ar', 'description_en']
    readonly_fields = ['id', 'current_usage_count', 'created_at', 'updated_at', 'time_remaining_display']
    filter_horizontal = ['applicable_products', 'applicable_categories']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name_en', 'name_ar', 'description_en', 'description_ar')
        }),
        ('Offer Configuration', {
            'fields': ('offer_type', 'buy_quantity', 'free_quantity', 'discount_type', 'discount_value')
        }),
        ('Product Restrictions', {
            'fields': ('applicable_products', 'applicable_categories')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'time_remaining_display')
        }),
        ('Usage Restrictions', {
            'fields': ('max_uses_per_customer', 'total_usage_limit', 'current_usage_count', 'minimum_order_amount')
        }),
        ('Display Settings', {
            'fields': ('button_text_en', 'button_text_ar', 'button_color', 'highlight_color', 'show_on_product_page', 'show_timer')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        now = timezone.now()
        if obj.is_running:
            color = 'green'
            status = 'Running'
        elif obj.is_upcoming:
            color = 'orange'
            status = 'Upcoming'
        elif obj.is_expired:
            color = 'red'
            status = 'Expired'
        else:
            color = 'gray'
            status = 'Inactive'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    status_badge.short_description = 'Status'
    
    def time_remaining_display(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        elif obj.is_upcoming:
            delta = obj.start_time - timezone.now()
            return format_html('<span style="color: orange;">Starts in: {}</span>', delta)
        elif obj.is_running and obj.end_time:
            delta = obj.end_time - timezone.now()
            return format_html('<span style="color: green;">Ends in: {}</span>', delta)
        elif obj.is_running:
            return format_html('<span style="color: green;">Running (no end time)</span>')
        else:
            return 'Not active'
    time_remaining_display.short_description = 'Time Remaining'


@admin.register(OfferUsage)
class OfferUsageAdmin(admin.ModelAdmin):
    list_display = [
        'offer_name', 'user_email', 'order_id', 'discount_amount', 
        'free_shipping_applied', 'created_at'
    ]
    list_filter = ['free_shipping_applied', 'created_at', 'flash_sale', 'special_offer']
    search_fields = ['user__email', 'order_id']
    readonly_fields = ['created_at']
    
    def offer_name(self, obj):
        if obj.flash_sale:
            return f"Flash Sale: {obj.flash_sale.name_en}"
        elif obj.special_offer:
            return f"Special Offer: {obj.special_offer.name_en}"
        return "Unknown"
    offer_name.short_description = 'Offer'
    
    def user_email(self, obj):
        return obj.user.email if obj.user else 'Guest'
    user_email.short_description = 'Customer'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(FlashSaleProduct)
class FlashSaleProductAdmin(admin.ModelAdmin):
    list_display = [
        'flash_sale', 'product', 'discount_type', 'discount_value',
        'discounted_price_display', 'quantity_limit', 'sold_quantity', 'is_featured'
    ]
    list_filter = ['flash_sale', 'discount_type', 'is_featured']
    search_fields = ['product__name_en', 'flash_sale__name_en']
    readonly_fields = ['sold_quantity', 'discounted_price_display', 'discount_amount_display']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('flash_sale', 'product')
        }),
        ('Discount Configuration', {
            'fields': ('discount_type', 'discount_value', 'discounted_price_display', 'discount_amount_display')
        }),
        ('Quantity Management', {
            'fields': ('quantity_limit', 'sold_quantity')
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'display_order')
        }),
    )
    
    def discounted_price_display(self, obj):
        return f"{obj.discounted_price} EGP"
    discounted_price_display.short_description = 'Discounted Price'
    
    def discount_amount_display(self, obj):
        return f"{obj.discount_amount} EGP"
    discount_amount_display.short_description = 'Discount Amount'


# Custom admin site configuration
admin.site.site_header = "Soleva Offers Management"
admin.site.site_title = "Soleva Admin"
admin.site.index_title = "Welcome to Soleva Administration"
