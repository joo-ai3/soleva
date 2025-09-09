from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Order, OrderItem, OrderStatusHistory, OrderPayment,
    OrderShipment, OrderRefund, PaymentProof
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    fields = [
        'product_name', 'product_sku', 'variant_attributes',
        'unit_price', 'quantity', 'total_price'
    ]


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['created_at']
    fields = ['previous_status', 'new_status', 'comment', 'changed_by', 'created_at']


class OrderPaymentInline(admin.TabularInline):
    model = OrderPayment
    extra = 0
    readonly_fields = ['created_at', 'processed_at']
    fields = [
        'payment_method', 'amount', 'status', 'gateway_transaction_id',
        'gateway_response', 'created_at', 'processed_at'
    ]


class PaymentProofInline(admin.TabularInline):
    model = PaymentProof
    extra = 0
    readonly_fields = ['image_preview', 'file_size_mb', 'created_at', 'verified_at']
    fields = [
        'image_preview', 'original_filename', 'file_size_mb',
        'verification_status', 'verification_notes', 'description',
        'uploaded_by', 'verified_by', 'created_at', 'verified_at'
    ]

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'payment_status', 'payment_method',
        'total_amount', 'has_payment_proof', 'created_at'
    ]
    list_filter = [
        'status', 'payment_status', 'payment_method', 'created_at',
        'payment_proofs__verification_status'
    ]
    search_fields = [
        'order_number', 'user__email', 'customer_email', 'customer_name',
        'customer_phone'
    ]
    readonly_fields = [
        'order_number', 'is_paid', 'can_be_cancelled', 'full_shipping_address',
        'created_at', 'updated_at'
    ]
    
    inlines = [OrderItemInline, PaymentProofInline, OrderStatusHistoryInline, OrderPaymentInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': (
                'order_number', 'user', 'status', 'payment_status', 'fulfillment_status',
                'created_at', 'updated_at'
            )
        }),
        ('Customer Information', {
            'fields': (
                'customer_email', 'customer_phone', 'customer_name'
            )
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_name', 'shipping_phone', 'shipping_address_line1',
                'shipping_address_line2', 'shipping_city', 'shipping_governorate',
                'shipping_postal_code', 'full_shipping_address'
            )
        }),
        ('Billing Address', {
            'fields': (
                'billing_name', 'billing_phone', 'billing_address_line1',
                'billing_address_line2', 'billing_city', 'billing_governorate',
                'billing_postal_code'
            ),
            'classes': ('collapse',)
        }),
        ('Order Totals', {
            'fields': (
                'subtotal', 'shipping_cost', 'tax_amount', 'discount_amount', 'total_amount'
            )
        }),
        ('Payment & Shipping', {
            'fields': (
                'payment_method', 'payment_reference', 'shipping_method',
                'tracking_number', 'courier_company', 'estimated_delivery_date'
            )
        }),
        ('Coupon', {
            'fields': ('coupon_code', 'coupon_discount'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes', 'language'),
            'classes': ('collapse',)
        }),
        ('Status Information', {
            'fields': (
                'is_paid', 'can_be_cancelled', 'confirmed_at', 'shipped_at',
                'delivered_at', 'cancelled_at'
            ),
            'classes': ('collapse',)
        })
    )

    def has_payment_proof(self, obj):
        count = obj.payment_proofs.count()
        if count == 0:
            return format_html('<span style="color: red;">No</span>')
        
        verified_count = obj.payment_proofs.filter(verification_status='verified').count()
        pending_count = obj.payment_proofs.filter(verification_status='pending').count()
        
        if verified_count > 0:
            return format_html('<span style="color: green;">✓ Verified ({})</span>', verified_count)
        elif pending_count > 0:
            return format_html('<span style="color: orange;">⏳ Pending ({})</span>', pending_count)
        else:
            return format_html('<span style="color: red;">✗ Rejected ({})</span>', count)
    
    has_payment_proof.short_description = "Payment Proof"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('payment_proofs')


@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order_link', 'image_preview', 'verification_status',
        'uploaded_by', 'created_at'
    ]
    list_filter = [
        'verification_status', 'created_at', 'verified_at'
    ]
    search_fields = [
        'order__order_number', 'original_filename', 'description',
        'uploaded_by__email'
    ]
    readonly_fields = [
        'image_preview_large', 'file_size', 'file_size_mb', 'upload_ip',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Payment Proof Information', {
            'fields': (
                'order', 'image_preview_large', 'original_filename',
                'file_size', 'file_size_mb', 'description'
            )
        }),
        ('Upload Information', {
            'fields': (
                'uploaded_by', 'upload_ip', 'created_at', 'updated_at'
            )
        }),
        ('Verification', {
            'fields': (
                'verification_status', 'verification_notes',
                'verified_by', 'verified_at'
            )
        })
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 75px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 400px;" />',
                obj.image.url
            )
        return "No image"
    image_preview_large.short_description = "Payment Proof"

    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.pk])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = "Order"

    def save_model(self, request, obj, form, change):
        if change and 'verification_status' in form.changed_data:
            # Update verified_by and verified_at when verification status changes
            from django.utils import timezone
            obj.verified_by = request.user
            obj.verified_at = timezone.now()
            
            # Update order payment status based on verification result
            if obj.verification_status == 'verified':
                order = obj.order
                order.payment_status = 'payment_approved'
                order.save()
            elif obj.verification_status == 'rejected':
                order = obj.order
                order.payment_status = 'payment_rejected'
                order.save()
        
        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product_name', 'quantity', 'unit_price', 'total_price']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['product_name', 'product_sku', 'order__order_number']


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'previous_status', 'new_status', 'changed_by', 'created_at']
    list_filter = ['new_status', 'created_at']
    search_fields = ['order__order_number', 'comment']
    readonly_fields = ['created_at']


@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'payment_method', 'amount', 'status', 'created_at']
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['order__order_number', 'gateway_transaction_id']
    readonly_fields = ['created_at', 'processed_at']


@admin.register(OrderShipment)
class OrderShipmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'tracking_number', 'status', 'shipped_at']
    list_filter = ['status', 'shipped_at']
    search_fields = ['order__order_number', 'tracking_number']


@admin.register(OrderRefund)
class OrderRefundAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'reason']
    readonly_fields = ['created_at']
