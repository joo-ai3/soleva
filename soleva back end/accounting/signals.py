"""
Accounting signals to automatically sync data with e-commerce operations
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from decimal import Decimal
from orders.models import Order, OrderItem
from products.models import Product
from .models import (
    SalesRecord, InventoryTransaction, ProductCost,
    Invoice, ShippingLabel
)


@receiver(post_save, sender=Order)
def create_sales_record(sender, instance, created, **kwargs):
    """Automatically create sales record when order is completed"""
    if instance.status == 'completed' and instance.payment_status in ['paid', 'payment_approved']:
        # Check if sales record already exists
        if not hasattr(instance, 'sales_record'):
            # Calculate total cost of goods sold
            total_cogs = Decimal('0.00')
            for item in instance.items.all():
                try:
                    product_cost = item.product.cost_info
                    item_cogs = product_cost.total_cost * item.quantity
                    total_cogs += item_cogs
                except ProductCost.DoesNotExist:
                    # If no cost info, use a default or skip
                    continue
            
            # Create sales record
            SalesRecord.objects.create(
                order=instance,
                gross_revenue=instance.total_amount,
                total_cost_of_goods=total_cogs,
                shipping_cost=instance.shipping_cost or Decimal('0.00'),
                packaging_cost=Decimal('0.00'),  # Will be calculated based on items
                payment_gateway_fee=Decimal('0.00'),  # Based on payment method
                discount_amount=instance.discount_amount or Decimal('0.00'),
                coupon_discount=instance.coupon_amount or Decimal('0.00'),
                sale_date=instance.created_at
            )


@receiver(post_save, sender=Order)
def create_inventory_transactions(sender, instance, created, **kwargs):
    """Create inventory transactions when order is placed"""
    if instance.status == 'confirmed':
        for item in instance.items.all():
            # Get current stock
            current_stock = item.product.stock_quantity
            new_stock = current_stock - item.quantity
            
            # Create inventory transaction
            InventoryTransaction.objects.create(
                product=item.product,
                variant=item.variant if hasattr(item, 'variant') else None,
                transaction_type='sale',
                quantity=-item.quantity,  # Negative for outgoing
                previous_stock=current_stock,
                new_stock=new_stock,
                unit_cost=getattr(item.product.cost_info, 'total_cost', None) if hasattr(item.product, 'cost_info') else None,
                total_cost=getattr(item.product.cost_info, 'total_cost', Decimal('0.00')) * item.quantity if hasattr(item.product, 'cost_info') else None,
                order=instance,
                reference_number=instance.order_number,
                notes=f'Sale from order {instance.order_number}'
            )
            
            # Update product stock
            item.product.stock_quantity = new_stock
            item.product.save(update_fields=['stock_quantity'])


@receiver(post_save, sender=Order)
def auto_generate_invoice(sender, instance, created, **kwargs):
    """Auto-generate invoice when order is confirmed"""
    if instance.status == 'confirmed' and not hasattr(instance, 'invoices'):
        invoice = Invoice.objects.create(
            order=instance,
            invoice_number=Invoice().generate_invoice_number(),
            issue_date=instance.created_at.date(),
            due_date=instance.created_at.date(),  # Immediate for e-commerce
            subtotal=instance.subtotal or instance.total_amount,
            tax_amount=Decimal('0.00'),  # Egypt typically includes tax in price
            shipping_amount=instance.shipping_cost or Decimal('0.00'),
            discount_amount=instance.discount_amount or Decimal('0.00'),
            total_amount=instance.total_amount,
            status='sent'
        )
        # Generate PDF will be handled by a separate task


@receiver(post_save, sender=Order)
def auto_generate_shipping_label(sender, instance, created, **kwargs):
    """Auto-generate shipping label when order needs shipping"""
    if instance.status in ['confirmed', 'processing'] and instance.shipping_address:
        if not hasattr(instance, 'shipping_label'):
            shipping_label = ShippingLabel.objects.create(
                order=instance,
                label_number=ShippingLabel().generate_label_number(),
                recipient_name=f"{instance.shipping_address.get('first_name', '')} {instance.shipping_address.get('last_name', '')}".strip(),
                recipient_phone=instance.shipping_address.get('phone', ''),
                delivery_address=f"{instance.shipping_address.get('address_line_1', '')}, {instance.shipping_address.get('address_line_2', '')}".strip(', '),
                governorate=instance.shipping_address.get('governorate', ''),
                city=instance.shipping_address.get('city', ''),
                postal_code=instance.shipping_address.get('postal_code', ''),
                shipping_cost=instance.shipping_cost or Decimal('0.00'),
                cash_on_delivery=instance.total_amount if instance.payment_method == 'cash_on_delivery' else Decimal('0.00'),
                shipping_method=instance.shipping_method or 'Standard Shipping'
            )


@receiver(post_save, sender=ProductCost)
def update_existing_inventory_costs(sender, instance, created, **kwargs):
    """Update inventory transaction costs when product cost is updated"""
    if not created:  # Only on updates, not creation
        # Update future inventory transactions
        InventoryTransaction.objects.filter(
            product=instance.product,
            unit_cost__isnull=True
        ).update(
            unit_cost=instance.total_cost
        )


# Low stock alert signal
@receiver(post_save, sender=InventoryTransaction)
def check_low_stock_alert(sender, instance, created, **kwargs):
    """Send low stock alerts when inventory falls below threshold"""
    if created and instance.transaction_type in ['sale', 'damaged']:
        LOW_STOCK_THRESHOLD = 10  # Can be made configurable
        
        if instance.new_stock <= LOW_STOCK_THRESHOLD:
            # Send notification (email, dashboard alert, etc.)
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = f"⚠️ Low Stock Alert: {instance.product.name}"
            message = f"""
            Product: {instance.product.name}
            Current Stock: {instance.new_stock}
            Threshold: {LOW_STOCK_THRESHOLD}
            
            Please reorder inventory.
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    ['inventory@thesoleva.com'],  # Configure admin emails
                    fail_silently=True,
                )
            except Exception:
                pass  # Handle email failure gracefully
