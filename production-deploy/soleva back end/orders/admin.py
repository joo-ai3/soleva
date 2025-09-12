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
    
    def save_model(self, request, obj, form, change):
        """Override save to track status changes and create history"""
        if change:
            # Get the original object from the database
            original = Order.objects.get(pk=obj.pk)
            old_status = original.status
            old_payment_status = original.payment_status
            
            # Save the object first
            super().save_model(request, obj, form, change)
            
            # Create status history if status changed
            if obj.status != old_status:
                from .models import OrderStatusHistory
                OrderStatusHistory.objects.create(
                    order=obj,
                    previous_status=old_status,
                    new_status=obj.status,
                    comment=f'Status updated by admin: {request.user.username}',
                    changed_by=request.user
                )
                
                # Update relevant timestamps
                from django.utils import timezone
                if obj.status == 'confirmed' and not obj.confirmed_at:
                    obj.confirmed_at = timezone.now()
                elif obj.status == 'shipped' and not obj.shipped_at:
                    obj.shipped_at = timezone.now()
                elif obj.status == 'delivered' and not obj.delivered_at:
                    obj.delivered_at = timezone.now()
                elif obj.status == 'cancelled' and not obj.cancelled_at:
                    obj.cancelled_at = timezone.now()
                
                obj.save(update_fields=['confirmed_at', 'shipped_at', 'delivered_at', 'cancelled_at'])
                
            # Handle payment status changes
            if obj.payment_status != old_payment_status and obj.payment_status == 'payment_approved':
                # Auto-confirm order when payment is approved
                if obj.status == 'pending':
                    obj.status = 'confirmed'
                    if not obj.confirmed_at:
                        obj.confirmed_at = timezone.now()
                    obj.save(update_fields=['status', 'confirmed_at'])
                    
                    # Create status history for auto-confirmation
                    OrderStatusHistory.objects.create(
                        order=obj,
                        previous_status='pending',
                        new_status='confirmed',
                        comment='Auto-confirmed after payment approval',
                        changed_by=request.user
                    )
        else:
            super().save_model(request, obj, form, change)
    
    # Custom admin actions
    actions = ['mark_as_confirmed', 'mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_confirmed(self, request, queryset):
        """Mark selected orders as confirmed"""
        from .models import OrderStatusHistory
        from django.utils import timezone
        
        updated = 0
        for order in queryset.filter(status='pending'):
            order.status = 'confirmed'
            order.confirmed_at = timezone.now()
            order.save()
            
            OrderStatusHistory.objects.create(
                order=order,
                previous_status='pending',
                new_status='confirmed',
                comment=f'Bulk confirmed by admin: {request.user.username}',
                changed_by=request.user
            )
            updated += 1
            
        self.message_user(request, f'{updated} orders marked as confirmed.')
    mark_as_confirmed.short_description = "Mark selected orders as confirmed"
    
    def mark_as_processing(self, request, queryset):
        """Mark selected orders as processing"""
        from .models import OrderStatusHistory
        
        updated = 0
        for order in queryset.filter(status='confirmed'):
            order.status = 'processing'
            order.save()
            
            OrderStatusHistory.objects.create(
                order=order,
                previous_status='confirmed',
                new_status='processing',
                comment=f'Bulk processing by admin: {request.user.username}',
                changed_by=request.user
            )
            updated += 1
            
        self.message_user(request, f'{updated} orders marked as processing.')
    mark_as_processing.short_description = "Mark selected orders as processing"
    
    def mark_as_shipped(self, request, queryset):
        """Mark selected orders as shipped"""
        from .models import OrderStatusHistory
        from django.utils import timezone
        
        updated = 0
        for order in queryset.filter(status='processing'):
            order.status = 'shipped'
            order.shipped_at = timezone.now()
            order.save()
            
            OrderStatusHistory.objects.create(
                order=order,
                previous_status='processing',
                new_status='shipped',
                comment=f'Bulk shipped by admin: {request.user.username}',
                changed_by=request.user
            )
            updated += 1
            
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_as_delivered(self, request, queryset):
        """Mark selected orders as delivered"""
        from .models import OrderStatusHistory
        from django.utils import timezone
        
        updated = 0
        for order in queryset.filter(status__in=['shipped', 'out_for_delivery']):
            order.status = 'delivered'
            order.delivered_at = timezone.now()
            order.save()
            
            OrderStatusHistory.objects.create(
                order=order,
                previous_status=order.status,
                new_status='delivered',
                comment=f'Bulk delivered by admin: {request.user.username}',
                changed_by=request.user
            )
            updated += 1
            
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_as_delivered.short_description = "Mark selected orders as delivered"


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
