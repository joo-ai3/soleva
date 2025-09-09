"""
Stripe payment gateway integration
"""

import stripe
from typing import Dict, Any
from decimal import Decimal
from django.conf import settings

from .base import BasePaymentGateway, PaymentResult


class StripeGateway(BasePaymentGateway):
    """Stripe payment gateway"""
    
    def __init__(self):
        super().__init__()
        self.secret_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
        self.publishable_key = getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')
        self.webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        
        if not self.secret_key:
            raise ValueError("Stripe secret key is required")
        
        stripe.api_key = self.secret_key
    
    def get_gateway_name(self) -> str:
        return 'stripe'
    
    def get_supported_currencies(self) -> list:
        return ['USD', 'EUR', 'EGP']
    
    def create_payment_intent(self, amount: Decimal, currency: str, order_data: Dict[str, Any]) -> PaymentResult:
        """Create Stripe payment intent"""
        if not self.validate_amount(amount, currency):
            return PaymentResult(success=False, error="Invalid payment amount")
        
        try:
            # Create customer if needed
            customer_data = {
                'email': order_data.get('customer_email'),
                'name': order_data.get('customer_name'),
                'phone': order_data.get('customer_phone'),
            }
            
            customer = stripe.Customer.create(**{k: v for k, v in customer_data.items() if v})
            
            # Create payment intent
            intent_data = {
                'amount': self.format_amount_for_gateway(amount, currency),
                'currency': currency.lower(),
                'customer': customer.id,
                'metadata': {
                    'order_number': order_data.get('order_number', ''),
                    'order_id': order_data.get('order_id', ''),
                },
                'automatic_payment_methods': {
                    'enabled': True,
                },
            }
            
            # Add shipping address if available
            shipping_address = order_data.get('shipping_address')
            if shipping_address:
                intent_data['shipping'] = {
                    'name': shipping_address.get('full_name', ''),
                    'phone': shipping_address.get('phone_number', ''),
                    'address': {
                        'line1': shipping_address.get('street_address', ''),
                        'line2': shipping_address.get('building_number', ''),
                        'city': shipping_address.get('city', ''),
                        'state': shipping_address.get('governorate', ''),
                        'postal_code': shipping_address.get('postal_code', ''),
                        'country': 'EG',
                    }
                }
            
            payment_intent = stripe.PaymentIntent.create(**intent_data)
            
            return PaymentResult(
                success=True,
                data={
                    'payment_intent_id': payment_intent.id,
                    'client_secret': payment_intent.client_secret,
                    'customer_id': customer.id,
                    'status': payment_intent.status,
                    'gateway_response': payment_intent
                }
            )
            
        except stripe.error.StripeError as e:
            return PaymentResult(success=False, error=str(e))
        except Exception as e:
            return self.handle_error(e, "create_payment_intent")
    
    def capture_payment(self, payment_intent_id: str, amount: Decimal = None) -> PaymentResult:
        """Capture Stripe payment intent"""
        try:
            capture_data = {}
            if amount:
                capture_data['amount_to_capture'] = self.format_amount_for_gateway(amount, 'USD')  # Assume USD for now
            
            payment_intent = stripe.PaymentIntent.capture(payment_intent_id, **capture_data)
            
            return PaymentResult(
                success=True,
                data={
                    'payment_intent_id': payment_intent.id,
                    'status': payment_intent.status,
                    'amount_captured': self.parse_amount_from_gateway(
                        payment_intent.amount_received, 
                        payment_intent.currency.upper()
                    ),
                    'gateway_response': payment_intent
                }
            )
            
        except stripe.error.StripeError as e:
            return PaymentResult(success=False, error=str(e))
        except Exception as e:
            return self.handle_error(e, "capture_payment")
    
    def refund_payment(self, transaction_id: str, amount: Decimal, reason: str = None) -> PaymentResult:
        """Refund Stripe payment"""
        try:
            refund_data = {
                'payment_intent': transaction_id,
            }
            
            if amount:
                # Get payment intent to determine currency
                payment_intent = stripe.PaymentIntent.retrieve(transaction_id)
                refund_data['amount'] = self.format_amount_for_gateway(amount, payment_intent.currency.upper())
            
            if reason:
                refund_data['reason'] = 'requested_by_customer'  # Stripe has limited reason options
                refund_data['metadata'] = {'reason': reason}
            
            refund = stripe.Refund.create(**refund_data)
            
            return PaymentResult(
                success=True,
                data={
                    'refund_id': refund.id,
                    'status': refund.status,
                    'amount': self.parse_amount_from_gateway(refund.amount, refund.currency.upper()),
                    'gateway_response': refund
                }
            )
            
        except stripe.error.StripeError as e:
            return PaymentResult(success=False, error=str(e))
        except Exception as e:
            return self.handle_error(e, "refund_payment")
    
    def get_payment_status(self, payment_intent_id: str) -> PaymentResult:
        """Get Stripe payment status"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Map Stripe status to our status
            status_mapping = {
                'requires_payment_method': 'pending',
                'requires_confirmation': 'pending',
                'requires_action': 'pending',
                'processing': 'processing',
                'requires_capture': 'processing',
                'canceled': 'cancelled',
                'succeeded': 'completed',
            }
            
            status = status_mapping.get(payment_intent.status, 'pending')
            
            return PaymentResult(
                success=True,
                data={
                    'status': status,
                    'amount': self.parse_amount_from_gateway(
                        payment_intent.amount, 
                        payment_intent.currency.upper()
                    ),
                    'amount_received': self.parse_amount_from_gateway(
                        payment_intent.amount_received, 
                        payment_intent.currency.upper()
                    ),
                    'currency': payment_intent.currency.upper(),
                    'gateway_response': payment_intent
                }
            )
            
        except stripe.error.StripeError as e:
            return PaymentResult(success=False, error=str(e))
        except Exception as e:
            return self.handle_error(e, "get_payment_status")
    
    def handle_webhook(self, webhook_data: Dict[str, Any], headers: Dict[str, str] = None) -> PaymentResult:
        """Handle Stripe webhook"""
        try:
            event_type = webhook_data.get('type')
            data = webhook_data.get('data', {}).get('object', {})
            
            if event_type in ['payment_intent.succeeded', 'payment_intent.payment_failed']:
                payment_intent_id = data.get('id')
                
                # Determine status
                if event_type == 'payment_intent.succeeded':
                    status = 'completed'
                else:
                    status = 'failed'
                
                return PaymentResult(
                    success=True,
                    data={
                        'transaction_id': payment_intent_id,
                        'gateway_transaction_id': payment_intent_id,
                        'status': status,
                        'amount': self.parse_amount_from_gateway(
                            data.get('amount', 0), 
                            data.get('currency', 'usd').upper()
                        ),
                        'currency': data.get('currency', 'usd').upper(),
                        'event_type': event_type,
                        'gateway_response': webhook_data
                    }
                )
            
            # Handle other event types as needed
            return PaymentResult(
                success=True,
                data={
                    'event_type': event_type,
                    'message': f'Webhook event {event_type} processed',
                    'gateway_response': webhook_data
                }
            )
            
        except Exception as e:
            return self.handle_error(e, "handle_webhook")
    
    def verify_webhook_signature(self, payload: str, signature: str, headers: Dict[str, str] = None) -> bool:
        """Verify Stripe webhook signature"""
        try:
            if not self.webhook_secret:
                return True  # Skip verification if no secret configured
            
            stripe.Webhook.construct_event(payload, signature, self.webhook_secret)
            return True
            
        except (stripe.error.SignatureVerificationError, ValueError):
            return False
        except Exception:
            return False
    
    def get_payment_url(self, payment_intent_id: str) -> str:
        """Get payment URL (for hosted checkout)"""
        # Stripe typically uses client-side integration
        # This would be used for hosted checkout sessions
        return None
