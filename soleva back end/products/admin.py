from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import (
    Category, Brand, Product, ProductImage, ProductAttribute,
    ProductAttributeValue, ProductVariant, ProductVariantAttribute
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text_en', 'alt_text_ar', 'display_order', 'is_primary']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ['sku', 'price', 'inventory_quantity', 'is_active']
    readonly_fields = ['sku']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name_en', 'name_ar', 'parent', 'display_order', 
        'is_active', 'is_featured', 'products_count'
    ]
    list_filter = ['is_active', 'is_featured', 'parent', 'created_at']
    search_fields = ['name_en', 'name_ar', 'description_en', 'description_ar']
    ordering = ['display_order', 'name_en']
    prepopulated_fields = {'slug': ('name_en',)}
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name_en', 'name_ar', 'slug', 'parent')
        }),
        (_('Description'), {
            'fields': ('description_en', 'description_ar')
        }),
        (_('Display Settings'), {
            'fields': ('image', 'icon', 'display_order', 'is_active', 'is_featured')
        }),
        (_('SEO'), {
            'fields': (
                'meta_title_en', 'meta_title_ar',
                'meta_description_en', 'meta_description_ar'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def products_count(self, obj):
        return obj.products.filter(is_active=True).count()
    products_count.short_description = _('Products Count')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'is_active', 'is_featured', 'products_count', 'created_at'
    ]
    list_filter = ['is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'description', 'logo', 'website')
        }),
        (_('Settings'), {
            'fields': ('is_active', 'is_featured')
        }),
    )
    
    def products_count(self, obj):
        return obj.products.filter(is_active=True).count()
    products_count.short_description = _('Products Count')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name_en', 'sku', 'category', 'brand', 'price', 
        'inventory_status', 'is_active', 'is_featured', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_featured', 'is_digital', 'category', 
        'brand', 'created_at', 'track_inventory'
    ]
    search_fields = ['name_en', 'name_ar', 'sku', 'description_en']
    ordering = ['-created_at']
    prepopulated_fields = {'slug': ('name_en',)}
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'name_en', 'name_ar', 'slug', 'sku',
                'category', 'brand'
            )
        }),
        (_('Description'), {
            'fields': (
                'short_description_en', 'short_description_ar',
                'description_en', 'description_ar'
            )
        }),
        (_('Pricing'), {
            'fields': ('price', 'compare_price', 'cost_price')
        }),
        (_('Inventory'), {
            'fields': (
                'track_inventory', 'inventory_quantity', 'low_stock_threshold'
            )
        }),
        (_('Physical Attributes'), {
            'fields': ('weight', 'length', 'width', 'height'),
            'classes': ('collapse',)
        }),
        (_('Settings'), {
            'fields': (
                'is_active', 'is_featured', 'is_digital', 
                'requires_shipping', 'display_order'
            )
        }),
        (_('SEO'), {
            'fields': (
                'meta_title_en', 'meta_title_ar',
                'meta_description_en', 'meta_description_ar'
            ),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('published_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['sku']
    
    def inventory_status(self, obj):
        if not obj.track_inventory:
            return format_html('<span style="color: green;">∞ Not Tracked</span>')
        elif obj.inventory_quantity == 0:
            return format_html('<span style="color: red;">⚠ Out of Stock</span>')
        elif obj.is_low_stock:
            return format_html(
                '<span style="color: orange;">⚠ Low Stock ({})</span>',
                obj.inventory_quantity
            )
        else:
            return format_html(
                '<span style="color: green;">✓ In Stock ({})</span>',
                obj.inventory_quantity
            )
    inventory_status.short_description = _('Inventory Status')
    
    def save_model(self, request, obj, form, change):
        if not obj.sku:
            # SKU will be auto-generated in the model's save method
            pass
        super().save_model(request, obj, form, change)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'display_order', 'is_primary', 'image_preview']
    list_filter = ['is_primary', 'product__category']
    search_fields = ['product__name_en', 'alt_text_en']
    ordering = ['product', 'display_order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = _('Preview')


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1
    fields = ['value_en', 'value_ar', 'color_code', 'display_order']


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = [
        'name_en', 'name_ar', 'attribute_type', 
        'is_required', 'is_filterable', 'display_order'
    ]
    list_filter = ['attribute_type', 'is_required', 'is_filterable']
    search_fields = ['name_en', 'name_ar']
    ordering = ['display_order', 'name_en']
    prepopulated_fields = {'slug': ('name_en',)}
    inlines = [ProductAttributeValueInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name_en', 'name_ar', 'slug', 'attribute_type')
        }),
        (_('Settings'), {
            'fields': ('is_required', 'is_filterable', 'display_order')
        }),
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'sku', 'effective_price', 'inventory_quantity', 
        'is_active', 'attributes_display'
    ]
    list_filter = ['is_active', 'product__category', 'product__brand']
    search_fields = ['sku', 'product__name_en']
    ordering = ['product', 'sku']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('product', 'sku')
        }),
        (_('Pricing'), {
            'fields': ('price', 'compare_price', 'cost_price')
        }),
        (_('Inventory & Physical'), {
            'fields': ('inventory_quantity', 'weight', 'image')
        }),
        (_('Settings'), {
            'fields': ('is_active',)
        }),
    )
    
    def attributes_display(self, obj):
        """Display variant attributes"""
        attributes = obj.attribute_values.select_related('attribute', 'value').all()
        if attributes:
            return ', '.join([
                f"{attr.attribute.name_en}: {attr.value.value_en}"
                for attr in attributes
            ])
        return '-'
    attributes_display.short_description = _('Attributes')


@admin.register(ProductVariantAttribute)
class ProductVariantAttributeAdmin(admin.ModelAdmin):
    list_display = ['variant', 'attribute', 'value']
    list_filter = ['attribute']
    search_fields = ['variant__sku', 'variant__product__name_en']
