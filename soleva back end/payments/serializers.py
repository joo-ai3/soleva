from rest_framework import serializers
from decimal import Decimal
from .models import PaymentMethod, PaymentTransaction, PaymentRefund


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Payment method serializer"""
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'name', 'code', 'display_name_en', 'display_name_ar',
            'description', 'icon', 'min_amount', 'max_amount',
            'fixed_fee', 'percentage_fee', 'display_order'
        ]


class PaymentIntentSerializer(serializers.Serializer):
    """Payment intent creation serializer"""
    
    order_id = serializers.IntegerField()
    payment_method_code = serializers.CharField(max_length=50)
    return_url = serializers.URLField(required=False, allow_blank=True)
    
    def validate_payment_method_code(self, value):
        """Validate payment method exists and is active"""
        try:
            PaymentMethod.objects.get(code=value, is_active=True)
        except PaymentMethod.DoesNotExist:
            raise serializers.ValidationError("Invalid payment method.")
        return value
    
    def validate_order_id(self, value):
        """Validate order exists and belongs to user"""
        from orders.models import Order
        user = self.context['request'].user
        
        try:
            order = Order.objects.get(id=value, user=user)
            if order.payment_status == 'paid':
                raise serializers.ValidationError("Order is already paid.")
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")
        
        return value


class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Payment transaction serializer"""
    
    payment_method_name = serializers.CharField(source='payment_method.display_name_en', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    is_successful = serializers.ReadOnlyField()
    can_be_refunded = serializers.ReadOnlyField()
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'transaction_id', 'order', 'order_number',
            'payment_method', 'payment_method_name', 'amount', 'currency',
            'fees', 'net_amount', 'status', 'gateway_name',
            'gateway_transaction_id', 'gateway_reference',
            'customer_email', 'customer_phone', 'customer_name',
            'failure_reason', 'is_successful', 'can_be_refunded',
            'created_at', 'processed_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'transaction_id', 'fees', 'net_amount',
            'gateway_transaction_id', 'gateway_reference',
            'created_at', 'processed_at', 'completed_at'
        ]


class PaymentRefundSerializer(serializers.ModelSerializer):
    """Payment refund serializer"""
    
    transaction_id = serializers.CharField(source='transaction.transaction_id', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.full_name', read_only=True)
    
    class Meta:
        model = PaymentRefund
        fields = [
            'id', 'refund_id', 'transaction', 'transaction_id',
            'amount', 'currency', 'reason', 'status',
            'gateway_refund_id', 'processed_by', 'processed_by_name',
            'failure_reason', 'created_at', 'processed_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'refund_id', 'gateway_refund_id',
            'created_at', 'processed_at', 'completed_at'
        ]


class RefundRequestSerializer(serializers.Serializer):
    """Refund request serializer"""
    
    transaction_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    reason = serializers.CharField(max_length=500)
    
    def validate_transaction_id(self, value):
        """Validate transaction exists and can be refunded"""
        user = self.context['request'].user
        
        try:
            transaction = PaymentTransaction.objects.get(
                transaction_id=value,
                user=user
            )
            
            if not transaction.can_be_refunded:
                raise serializers.ValidationError("Transaction cannot be refunded.")
            
            self.context['transaction'] = transaction
            
        except PaymentTransaction.DoesNotExist:
            raise serializers.ValidationError("Transaction not found.")
        
        return value
    
    def validate_amount(self, value):
        """Validate refund amount"""
        transaction = self.context.get('transaction')
        
        if transaction and value:
            # Check if amount is valid
            if value <= 0:
                raise serializers.ValidationError("Refund amount must be greater than zero.")
            
            if value > transaction.amount:
                raise serializers.ValidationError("Refund amount cannot exceed transaction amount.")
            
            # Check previous refunds
            total_refunded = transaction.refunds.filter(
                status__in=['completed', 'processing']
            ).aggregate(
                total=serializers.Sum('amount')
            )['total'] or Decimal('0.00')
            
            if value + total_refunded > transaction.amount:
                remaining = transaction.amount - total_refunded
                raise serializers.ValidationError(
                    f"Refund amount exceeds remaining refundable amount ({remaining} {transaction.currency})."
                )
        
        return value
    
    def validate(self, attrs):
        """Validate refund request"""
        transaction = self.context.get('transaction')
        amount = attrs.get('amount')
        
        # If no amount specified, refund full remaining amount
        if not amount and transaction:
            total_refunded = transaction.refunds.filter(
                status__in=['completed', 'processing']
            ).aggregate(
                total=serializers.Sum('amount')
            )['total'] or Decimal('0.00')
            
            attrs['amount'] = transaction.amount - total_refunded
        
        return attrs


class PaymentCallbackSerializer(serializers.Serializer):
    """Payment callback/webhook serializer"""
    
    gateway_name = serializers.CharField()
    transaction_id = serializers.CharField(required=False, allow_blank=True)
    gateway_transaction_id = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    currency = serializers.CharField(max_length=3, default='EGP')
    
    # Gateway-specific fields
    paymob_order_id = serializers.CharField(required=False, allow_blank=True)
    paymob_transaction_id = serializers.CharField(required=False, allow_blank=True)
    stripe_payment_intent_id = serializers.CharField(required=False, allow_blank=True)
    
    # Additional data
    raw_data = serializers.JSONField(required=False, default=dict)


class PaymentStatsSerializer(serializers.Serializer):
    """Payment statistics serializer"""
    
    total_transactions = serializers.IntegerField()
    completed_transactions = serializers.IntegerField()
    failed_transactions = serializers.IntegerField()
    pending_transactions = serializers.IntegerField()
    
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    completed_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    total_refunds = serializers.IntegerField()
    refunded_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # By payment method
    payment_methods_stats = serializers.ListField(child=serializers.DictField())
    
    # Today's stats
    today_transactions = serializers.IntegerField()
    today_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Success rate
    success_rate = serializers.FloatField()
