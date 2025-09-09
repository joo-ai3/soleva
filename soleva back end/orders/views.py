from rest_framework import status, permissions, filters, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta, date
from decimal import Decimal

from .models import Order, OrderItem, OrderStatusHistory, PaymentProof
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer,
    OrderUpdateSerializer, OrderTrackingSerializer, OrderStatsSerializer,
    PaymentProofSerializer, PaymentProofUploadSerializer, PaymentProofVerificationSerializer
)
from cart.models import Cart, CartItem
from products.models import Product, ProductVariant
from coupons.models import Coupon, CouponUsage
from notifications.models import Notification

User = get_user_model()


class OrderViewSet(ModelViewSet):
    """Order management viewset"""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer_email', 'customer_name']
    ordering_fields = ['created_at', 'total_amount', 'order_number']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get orders based on user role"""
        if self.request.user.is_staff:
            # Admin can see all orders
            return Order.objects.all().prefetch_related('items', 'status_history')
        else:
            # Regular users see only their orders
            return Order.objects.filter(user=self.request.user).prefetch_related('items', 'status_history')
    
    def get_serializer_class(self):
        """Get appropriate serializer"""
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update'] and self.request.user.is_staff:
            return OrderUpdateSerializer
        return OrderDetailSerializer
    
    def get_permissions(self):
        """Get permissions based on action"""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """Create new order from cart"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                order = self._create_order_from_cart(request.user, serializer.validated_data)
                
                # Send order confirmation notification
                self._send_order_notification(order, 'order_confirmation')
                
                return Response({
                    'message': 'Order created successfully.',
                    'order': OrderDetailSerializer(order, context={'request': request}).data
                }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Update order (admin only)"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_status = instance.status
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            order = serializer.save()
            
            # Create status history entry if status changed
            if order.status != old_status:
                OrderStatusHistory.objects.create(
                    order=order,
                    previous_status=old_status,
                    new_status=order.status,
                    comment=request.data.get('status_comment', ''),
                    changed_by=request.user
                )
                
                # Send notification based on new status
                self._send_status_notification(order)
            
            return Response({
                'message': 'Order updated successfully.',
                'order': OrderDetailSerializer(order, context={'request': request}).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel order"""
        order = self.get_object()
        
        # Check if user can cancel this order
        if order.user != request.user and not request.user.is_staff:
            return Response({
                'error': 'You can only cancel your own orders.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not order.can_be_cancelled:
            return Response({
                'error': 'This order cannot be cancelled.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Cancel the order
        old_status = order.status
        order.status = 'cancelled'
        order.cancelled_at = timezone.now()
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            previous_status=old_status,
            new_status='cancelled',
            comment=request.data.get('reason', 'Cancelled by user'),
            changed_by=request.user
        )
        
        # Restore inventory (if needed)
        self._restore_inventory(order)
        
        # Send cancellation notification
        self._send_order_notification(order, 'order_cancelled')
        
        return Response({
            'message': 'Order cancelled successfully.',
            'order': OrderDetailSerializer(order, context={'request': request}).data
        })
    
    @action(detail=True, methods=['get'])
    def tracking(self, request, pk=None):
        """Get order tracking information"""
        order = self.get_object()
        
        # Check permissions
        if order.user != request.user and not request.user.is_staff:
            return Response({
                'error': 'Access denied.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Build timeline from status history
        timeline = []
        for history in order.status_history.all().order_by('created_at'):
            timeline.append({
                'status': history.new_status,
                'status_display': dict(Order.ORDER_STATUS_CHOICES).get(history.new_status, history.new_status),
                'timestamp': history.created_at,
                'comment': history.comment,
            })
        
        tracking_data = {
            'order_number': order.order_number,
            'status': order.status,
            'status_display': order.get_status_display(),
            'tracking_number': order.tracking_number,
            'courier_company': order.courier_company,
            'estimated_delivery_date': order.estimated_delivery_date,
            'timeline': timeline,
            'current_location': '',  # Would integrate with courier API
            'last_update': order.updated_at,
        }
        
        serializer = OrderTrackingSerializer(tracking_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """Reorder items from previous order"""
        order = self.get_object()
        
        # Check if user can reorder
        if order.user != request.user:
            return Response({
                'error': 'You can only reorder your own orders.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        added_items = []
        unavailable_items = []
        
        for item in order.items.all():
            try:
                # Check if product/variant is still available
                if item.variant_id:
                    variant = ProductVariant.objects.get(
                        id=item.variant_id, 
                        is_active=True,
                        product__is_active=True
                    )
                    if not variant.is_in_stock:
                        unavailable_items.append(item.product_name)
                        continue
                    
                    product = variant.product
                    price = variant.effective_price
                    image = variant.image.url if variant.image else ''
                else:
                    product = Product.objects.get(id=item.product_id, is_active=True)
                    if not product.is_in_stock:
                        unavailable_items.append(item.product_name)
                        continue
                    
                    price = product.price
                    image = product.images.filter(is_primary=True).first()
                    image = image.image.url if image else ''
                
                # Add to cart
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    defaults={
                        'quantity': item.quantity,
                        'product_name': item.product_name,
                        'product_price': price,
                        'product_image': image,
                        'variant_attributes': item.variant_attributes,
                    }
                )
                
                if not created:
                    cart_item.quantity += item.quantity
                    cart_item.save()
                
                added_items.append(item.product_name)
                
            except (Product.DoesNotExist, ProductVariant.DoesNotExist):
                unavailable_items.append(item.product_name)
        
        return Response({
            'message': f'Added {len(added_items)} items to cart.',
            'added_items': added_items,
            'unavailable_items': unavailable_items,
        })
    
    def _create_order_from_cart(self, user, validated_data):
        """Create order from user's cart"""
        cart = validated_data['cart']
        shipping_address = validated_data['shipping_address_id']
        billing_address = validated_data.get('billing_address_id') or shipping_address
        payment_method = validated_data['payment_method']
        customer_notes = validated_data.get('customer_notes', '')
        coupon = validated_data.get('coupon_code')
        
        # Calculate order totals
        subtotal = cart.subtotal
        shipping_cost = self._calculate_shipping_cost(cart, shipping_address)
        tax_amount = Decimal('0.00')  # No tax for now
        discount_amount = Decimal('0.00')
        coupon_discount = Decimal('0.00')
        
        if coupon:
            coupon_discount = coupon.calculate_discount(subtotal, shipping_cost)
            discount_amount = coupon_discount
        
        total_amount = subtotal + shipping_cost + tax_amount - discount_amount
        
        # Determine initial payment status based on payment method
        initial_payment_status = 'pending'
        if payment_method in ['bank_wallet', 'e_wallet']:
            initial_payment_status = 'pending_review'  # Wait for payment proof upload
        elif payment_method == 'cash_on_delivery':
            initial_payment_status = 'pending'  # Will be marked as paid on delivery
            
        # Create order
        order = Order.objects.create(
            user=user,
            customer_email=user.email,
            customer_phone=str(user.phone_number) if user.phone_number else '',
            customer_name=user.full_name,
            
            # Shipping address
            shipping_address_line1=shipping_address.street_address,
            shipping_address_line2=f"{shipping_address.building_number} {shipping_address.apartment_number}".strip(),
            shipping_city=shipping_address.city,
            shipping_governorate=shipping_address.governorate,
            shipping_postal_code=shipping_address.postal_code,
            shipping_phone=str(shipping_address.phone_number),
            shipping_name=shipping_address.full_name,
            
            # Billing address
            billing_address_line1=billing_address.street_address,
            billing_address_line2=f"{billing_address.building_number} {billing_address.apartment_number}".strip(),
            billing_city=billing_address.city,
            billing_governorate=billing_address.governorate,
            billing_postal_code=billing_address.postal_code,
            billing_phone=str(billing_address.phone_number),
            billing_name=billing_address.full_name,
            
            # Totals
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            
            # Payment & shipping
            payment_method=payment_method,
            payment_status=initial_payment_status,
            shipping_method='standard',
            
            # Coupon
            coupon_code=coupon.code if coupon else '',
            coupon_discount=coupon_discount,
            
            # Notes
            customer_notes=customer_notes,
            language=user.language_preference,
        )
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_id=cart_item.product_id,
                product_name=cart_item.product_name,
                product_sku=self._get_product_sku(cart_item),
                product_image=cart_item.product_image,
                variant_id=cart_item.variant_id,
                variant_sku=self._get_variant_sku(cart_item),
                variant_attributes=cart_item.variant_attributes,
                unit_price=cart_item.product_price,
                quantity=cart_item.quantity,
            )
        
        # Record coupon usage
        if coupon:
            CouponUsage.objects.create(
                coupon=coupon,
                user=user,
                order=order,
                discount_amount=coupon_discount,
                order_total=total_amount,
            )
            
            # Update coupon usage count
            coupon.used_count += 1
            coupon.save()
        
        # Clear cart
        cart.clear()
        
        # Create initial status history
        OrderStatusHistory.objects.create(
            order=order,
            previous_status='',
            new_status='pending',
            comment='Order created',
            changed_by=user
        )
        
        return order
    
    def _calculate_shipping_cost(self, cart, shipping_address):
        """Calculate shipping cost (simplified)"""
        # This would integrate with the shipping system
        # For now, return a fixed cost based on governorate
        base_cost = Decimal('30.00')  # Base shipping cost
        
        # Premium governorates (Cairo, Giza, Alexandria)
        premium_governorates = ['Cairo', 'Giza', 'Alexandria']
        if shipping_address.governorate in premium_governorates:
            return base_cost
        else:
            return base_cost + Decimal('10.00')  # Additional cost for other governorates
    
    def _get_product_sku(self, cart_item):
        """Get product SKU"""
        try:
            product = Product.objects.get(id=cart_item.product_id)
            return product.sku
        except Product.DoesNotExist:
            return ''
    
    def _get_variant_sku(self, cart_item):
        """Get variant SKU"""
        if cart_item.variant_id:
            try:
                variant = ProductVariant.objects.get(id=cart_item.variant_id)
                return variant.sku
            except ProductVariant.DoesNotExist:
                return ''
        return ''
    
    def _restore_inventory(self, order):
        """Restore inventory when order is cancelled"""
        for item in order.items.all():
            try:
                if item.variant_id:
                    variant = ProductVariant.objects.get(id=item.variant_id)
                    variant.inventory_quantity += item.quantity
                    variant.save()
                else:
                    product = Product.objects.get(id=item.product_id)
                    if product.track_inventory:
                        product.inventory_quantity += item.quantity
                        product.save()
            except (Product.DoesNotExist, ProductVariant.DoesNotExist):
                continue
    
    def _send_order_notification(self, order, notification_type):
        """Send order notification"""
        # Create notification record
        Notification.objects.create(
            user=order.user,
            notification_type=notification_type,
            title=f'Order {order.order_number}',
            message=f'Your order {order.order_number} has been {notification_type.replace("_", " ")}.',
            channel='email',
            recipient_email=order.customer_email,
            order=order,
        )
    
    def _send_status_notification(self, order):
        """Send status update notification"""
        status_messages = {
            'confirmed': 'has been confirmed',
            'processing': 'is being processed',
            'shipped': 'has been shipped',
            'out_for_delivery': 'is out for delivery',
            'delivered': 'has been delivered',
            'cancelled': 'has been cancelled',
        }
        
        # Payment status messages
        payment_status_messages = {
            'pending_review': 'is pending payment proof upload',
            'under_review': 'payment is under review',
            'payment_approved': 'payment has been approved',
            'payment_rejected': 'payment has been rejected',
            'paid': 'has been paid',
        }
        
        # Determine notification type and message
        if order.status in status_messages:
            message = status_messages.get(order.status)
            notification_type = f'order_{order.status}'
        elif hasattr(order, '_payment_status_changed') and order.payment_status in payment_status_messages:
            message = payment_status_messages.get(order.payment_status)
            notification_type = f'payment_{order.payment_status}'
        else:
            message = f'status updated to {order.status}'
            notification_type = 'order_updated'
        
        Notification.objects.create(
            user=order.user,
            notification_type=notification_type,
            title=f'Order {order.order_number} Update',
            message=f'Your order {order.order_number} {message}.',
            channel='email',
            recipient_email=order.customer_email,
            order=order,
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def order_stats(request):
    """Get order statistics"""
    if not request.user.is_staff:
        # Regular users get their own stats
        orders = Order.objects.filter(user=request.user)
    else:
        # Admin gets global stats
        orders = Order.objects.all()
    
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    stats = {
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status='pending').count(),
        'confirmed_orders': orders.filter(status='confirmed').count(),
        'shipped_orders': orders.filter(status='shipped').count(),
        'delivered_orders': orders.filter(status='delivered').count(),
        'cancelled_orders': orders.filter(status='cancelled').count(),
        
        'total_revenue': orders.filter(
            status__in=['delivered', 'shipped', 'confirmed']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00'),
        
        'average_order_value': orders.aggregate(
            avg=Avg('total_amount')
        )['avg'] or Decimal('0.00'),
        
        'today_orders': orders.filter(created_at__date=today).count(),
        'today_revenue': orders.filter(
            created_at__date=today,
            status__in=['delivered', 'shipped', 'confirmed']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00'),
        
        'month_orders': orders.filter(created_at__date__gte=month_start).count(),
        'month_revenue': orders.filter(
            created_at__date__gte=month_start,
            status__in=['delivered', 'shipped', 'confirmed']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00'),
    }
    
    serializer = OrderStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def track_order(request):
    """Track order by order number (public endpoint)"""
    order_number = request.GET.get('order_number', '').strip()
    email = request.GET.get('email', '').strip().lower()
    
    if not order_number or not email:
        return Response({
            'error': 'Order number and email are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order = Order.objects.get(
            order_number=order_number,
            customer_email__iexact=email
        )
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Build timeline
    timeline = []
    for history in order.status_history.all().order_by('created_at'):
        timeline.append({
            'status': history.new_status,
            'status_display': dict(Order.ORDER_STATUS_CHOICES).get(history.new_status, history.new_status),
            'timestamp': history.created_at,
            'comment': history.comment,
        })
    
    tracking_data = {
        'order_number': order.order_number,
        'status': order.status,
        'status_display': order.get_status_display(),
        'tracking_number': order.tracking_number,
        'courier_company': order.courier_company,
        'estimated_delivery_date': order.estimated_delivery_date,
        'timeline': timeline,
        'current_location': '',
        'last_update': order.updated_at,
    }
    
    serializer = OrderTrackingSerializer(tracking_data)
    return Response(serializer.data)


class PaymentProofViewSet(ModelViewSet):
    """Payment proof management viewset"""
    
    serializer_class = PaymentProofSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['verification_status']
    ordering_fields = ['created_at', 'verification_status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get payment proofs for user's orders or all if admin"""
        if self.request.user.is_staff:
            return PaymentProof.objects.all().select_related('order', 'uploaded_by', 'verified_by')
        else:
            return PaymentProof.objects.filter(
                order__user=self.request.user
            ).select_related('order', 'uploaded_by', 'verified_by')
    
    def get_serializer_class(self):
        """Get appropriate serializer class"""
        if self.action == 'create':
            return PaymentProofUploadSerializer
        elif self.action in ['verify_payment']:
            return PaymentProofVerificationSerializer
        return PaymentProofSerializer
    
    def get_permissions(self):
        """Get permissions based on action"""
        if self.action in ['verify_payment']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """Upload payment proof for an order"""
        order_id = request.data.get('order_id')
        
        if not order_id:
            return Response({
                'error': 'Order ID is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify order exists and belongs to user (or user is admin)
        try:
            if request.user.is_staff:
                order = Order.objects.get(id=order_id)
            else:
                order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({
                'error': 'Order not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if order uses bank wallet or e-wallet payment
        if order.payment_method not in ['bank_wallet', 'e_wallet']:
            return Response({
                'error': 'Payment proof is only required for Bank Wallet and E-Wallet payments.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if payment proof already exists
        if order.payment_proofs.exists():
            return Response({
                'error': 'Payment proof has already been uploaded for this order.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data, context={
            'request': request,
            'order_id': order.id
        })
        
        if serializer.is_valid():
            payment_proof = serializer.save()
            
            # Update order payment status to 'under_review' when proof is uploaded
            order.payment_status = 'under_review'
            order.save()
            
            # Create status history entry
            OrderStatusHistory.objects.create(
                order=order,
                previous_status=order.payment_status,
                new_status='under_review',
                comment='Payment proof uploaded, pending admin review',
                changed_by=request.user
            )
            
            # Send notification to admin about new payment proof
            try:
                admin_users = User.objects.filter(is_staff=True, is_active=True)
                for admin in admin_users:
                    Notification.objects.create(
                        user=admin,
                        title='New Payment Proof',
                        message=f'New payment proof uploaded for order {order.order_number}',
                        notification_type='payment_proof_uploaded'
                    )
            except:
                pass  # Notification is optional
                
            # Send notification to customer
            try:
                Notification.objects.create(
                    user=order.user,
                    title='Payment Proof Uploaded',
                    message=f'Your payment proof for order {order.order_number} has been uploaded and is under review.',
                    notification_type='payment_proof_submitted'
                )
            except:
                pass  # Notification is optional
            
            response_serializer = PaymentProofSerializer(payment_proof, context={'request': request})
            return Response({
                'message': 'Payment proof uploaded successfully. Your payment is now under review.',
                'payment_proof': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def verify_payment(self, request, pk=None):
        """Verify payment proof (admin only)"""
        payment_proof = self.get_object()
        serializer = PaymentProofVerificationSerializer(
            payment_proof, 
            data=request.data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            order = payment_proof.order
            
            # Update order payment status based on verification result
            if payment_proof.verification_status == 'verified':
                old_payment_status = order.payment_status
                order.payment_status = 'payment_approved'
                order.save()
                
                # Create status history entry
                OrderStatusHistory.objects.create(
                    order=order,
                    previous_status=old_payment_status,
                    new_status='payment_approved',
                    comment=f'Payment proof verified by admin: {request.user.email}',
                    changed_by=request.user
                )
                
                # Create notification for customer
                try:
                    Notification.objects.create(
                        user=order.user,
                        title='Payment Approved',
                        message=f'Your payment for order {order.order_number} has been approved and verified.',
                        notification_type='payment_approved'
                    )
                except:
                    pass  # Notification is optional
                    
            elif payment_proof.verification_status == 'rejected':
                old_payment_status = order.payment_status
                order.payment_status = 'payment_rejected'
                order.save()
                
                # Create status history entry
                OrderStatusHistory.objects.create(
                    order=order,
                    previous_status=old_payment_status,
                    new_status='payment_rejected',
                    comment=f'Payment proof rejected by admin: {request.user.email}. Notes: {payment_proof.verification_notes}',
                    changed_by=request.user
                )
                
                # Create notification for customer
                try:
                    Notification.objects.create(
                        user=order.user,
                        title='Payment Rejected',
                        message=f'Your payment for order {order.order_number} has been rejected. Please contact support for assistance.',
                        notification_type='payment_rejected'
                    )
                except:
                    pass  # Notification is optional
            
            return Response({
                'message': 'Payment proof verification updated successfully.',
                'payment_proof': PaymentProofSerializer(payment_proof, context={'request': request}).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_payment_proof(request, order_id):
    """Upload payment proof for a specific order"""
    try:
        if request.user.is_staff:
            order = Order.objects.get(id=order_id)
        else:
            order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if order uses bank wallet or e-wallet payment
    if order.payment_method not in ['bank_wallet', 'e_wallet']:
        return Response({
            'error': 'Payment proof is only required for Bank Wallet and E-Wallet payments.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if payment proof already exists
    if order.payment_proofs.exists():
        return Response({
            'error': 'Payment proof has already been uploaded for this order.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = PaymentProofUploadSerializer(data=request.data, context={
        'request': request,
        'order_id': order.id
    })
    
    if serializer.is_valid():
        payment_proof = serializer.save()
        response_serializer = PaymentProofSerializer(payment_proof, context={'request': request})
        return Response({
            'message': 'Payment proof uploaded successfully.',
            'payment_proof': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
