from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import PaymentMethod, PaymentTransaction, PaymentRefund, PaymentWebhook
from .serializers import (
    PaymentMethodSerializer, PaymentIntentSerializer, PaymentTransactionSerializer,
    PaymentRefundSerializer, RefundRequestSerializer, PaymentStatsSerializer
)
from .gateways import get_gateway
from orders.models import Order


class PaymentMethodListView(generics.ListAPIView):
    """List available payment methods"""
    
    queryset = PaymentMethod.objects.filter(is_active=True).order_by('display_order')
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.AllowAny]


class CreatePaymentIntentView(APIView):
    """Create payment intent"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PaymentIntentSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Implementation would go here
        return Response({'message': 'Payment intent creation not fully implemented'})


class CapturePaymentView(APIView):
    """Capture payment"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, payment_intent_id):
        # Implementation would go here
        return Response({'message': 'Payment capture not fully implemented'})


class PaymentStatusView(APIView):
    """Get payment status"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, payment_intent_id):
        # Implementation would go here
        return Response({'message': 'Payment status check not fully implemented'})


class RefundRequestView(APIView):
    """Request refund"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Implementation would go here
        return Response({'message': 'Refund request not fully implemented'})


class RefundListView(generics.ListAPIView):
    """List refunds"""
    
    serializer_class = PaymentRefundSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return PaymentRefund.objects.all().order_by('-created_at')
        return PaymentRefund.objects.filter(
            transaction__user=self.request.user
        ).order_by('-created_at')


class TransactionListView(generics.ListAPIView):
    """List transactions"""
    
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return PaymentTransaction.objects.all().select_related('user', 'payment_method').order_by('-created_at')
        return PaymentTransaction.objects.filter(
            user=self.request.user
        ).select_related('payment_method').order_by('-created_at')


class TransactionDetailView(generics.RetrieveAPIView):
    """Transaction detail"""
    
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'transaction_id'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return PaymentTransaction.objects.all()
        return PaymentTransaction.objects.filter(user=self.request.user)


class PaymobWebhookView(APIView):
    """Paymob webhook handler"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        # Implementation would go here
        return Response({'status': 'received'})


class StripeWebhookView(APIView):
    """Stripe webhook handler"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        # Implementation would go here
        return Response({'status': 'received'})


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def payment_stats(request):
    """Payment statistics"""
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    transactions = PaymentTransaction.objects.filter(created_at__gte=start_date)
    
    stats = {
        'total_transactions': transactions.count(),
        'completed_transactions': transactions.filter(status='completed').count(),
        'failed_transactions': transactions.filter(status='failed').count(),
        'pending_transactions': transactions.filter(status='pending').count(),
        
        'total_amount': transactions.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00'),
        
        'completed_amount': transactions.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00'),
        
        'total_refunds': PaymentRefund.objects.filter(created_at__gte=start_date).count(),
        'refunded_amount': PaymentRefund.objects.filter(
            created_at__gte=start_date,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        
        'payment_methods_stats': list(
            transactions.values('payment_method__name').annotate(
                count=Count('id'),
                amount=Sum('amount')
            ).order_by('-count')
        ),
        
        'today_transactions': transactions.filter(created_at__date=timezone.now().date()).count(),
        'today_amount': transactions.filter(
            created_at__date=timezone.now().date(),
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        
        'success_rate': 0.0,  # Calculate based on completed vs total
    }
    
    # Calculate success rate
    if stats['total_transactions'] > 0:
        stats['success_rate'] = (stats['completed_transactions'] / stats['total_transactions']) * 100
    
    serializer = PaymentStatsSerializer(stats)
    return Response(serializer.data)
