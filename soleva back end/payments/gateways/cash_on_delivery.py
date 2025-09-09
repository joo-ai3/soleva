"""
Cash on Delivery payment gateway
"""

from typing import Dict, Any
from decimal import Decimal

from .base import BasePaymentGateway, PaymentResult


class CashOnDeliveryGateway(BasePaymentGateway):
    """Cash on Delivery payment gateway"""
    
    def get_gateway_name(self) -> str:
        return 'cash_on_delivery'
    
    def get_supported_currencies(self) -> list:
        return ['EGP', 'USD', 'EUR']
    
    def create_payment_intent(self, amount: Decimal, currency: str, order_data: Dict[str, Any]) -> PaymentResult:
        """Create COD payment intent"""
        if not self.validate_amount(amount, currency):
            return PaymentResult(success=False, error="Invalid payment amount")
        
        # For COD, we just create a placeholder payment intent
        return PaymentResult(
            success=True,
            data={
                'payment_intent_id': f"cod_{order_data.get('order_number', 'unknown')}",
                'payment_method': 'cash_on_delivery',
                'status': 'pending',
                'amount': amount,
                'currency': currency,
                'message': 'Cash on Delivery order created. Payment will be collected upon delivery.'
            }
        )
    
    def capture_payment(self, payment_intent_id: str, amount: Decimal = None) -> PaymentResult:
        """Capture COD payment (mark as paid upon delivery)"""
        return PaymentResult(
            success=True,
            data={
                'payment_intent_id': payment_intent_id,
                'status': 'completed',
                'message': 'Cash on Delivery payment captured upon delivery'
            }
        )
    
    def refund_payment(self, transaction_id: str, amount: Decimal, reason: str = None) -> PaymentResult:
        """Refund COD payment (manual process)"""
        return PaymentResult(
            success=True,
            data={
                'refund_id': f"cod_refund_{transaction_id}",
                'status': 'pending',
                'message': 'COD refund initiated. Customer will be contacted for refund process.',
                'manual_process_required': True
            }
        )
    
    def get_payment_status(self, payment_intent_id: str) -> PaymentResult:
        """Get COD payment status"""
        # COD payments are typically pending until delivery
        return PaymentResult(
            success=True,
            data={
                'status': 'pending',
                'message': 'Cash on Delivery payment pending until delivery'
            }
        )
    
    def handle_webhook(self, webhook_data: Dict[str, Any], headers: Dict[str, str] = None) -> PaymentResult:
        """Handle COD webhook (not applicable)"""
        return PaymentResult(
            success=True,
            data={
                'message': 'COD does not use webhooks'
            }
        )
    
    def verify_webhook_signature(self, payload: str, signature: str, headers: Dict[str, str] = None) -> bool:
        """Verify COD webhook signature (always true as COD doesn't use webhooks)"""
        return True
    
    def get_minimum_amount(self, currency: str = 'EGP') -> Decimal:
        """Get minimum COD amount"""
        # COD might have higher minimums due to delivery costs
        minimums = {
            'EGP': Decimal('50.00'),  # Minimum 50 EGP for COD
            'USD': Decimal('5.00'),   # Minimum 5 USD for COD
            'EUR': Decimal('5.00'),   # Minimum 5 EUR for COD
        }
        return minimums.get(currency, Decimal('50.00'))
    
    def get_maximum_amount(self, currency: str = 'EGP') -> Decimal:
        """Get maximum COD amount"""
        # COD might have lower maximums due to risk
        maximums = {
            'EGP': Decimal('10000.00'),  # Maximum 10K EGP for COD
            'USD': Decimal('1000.00'),   # Maximum 1K USD for COD
            'EUR': Decimal('1000.00'),   # Maximum 1K EUR for COD
        }
        return maximums.get(currency, Decimal('10000.00'))
