"""
Paymob payment gateway integration
"""

import requests
import hashlib
import hmac
from typing import Dict, Any
from decimal import Decimal
from django.conf import settings

from .base import BasePaymentGateway, PaymentResult


class PaymobGateway(BasePaymentGateway):
    """Paymob payment gateway"""
    
    def __init__(self):
        super().__init__()
        self.api_key = getattr(settings, 'PAYMOB_API_KEY', '')
        self.secret_key = getattr(settings, 'PAYMOB_SECRET_KEY', '')
        self.integration_id = getattr(settings, 'PAYMOB_INTEGRATION_ID', '')
        self.base_url = 'https://accept.paymob.com/api'
        
        if not all([self.api_key, self.secret_key]):
            raise ValueError("Paymob API key and secret key are required")
    
    def get_gateway_name(self) -> str:
        return 'paymob'
    
    def get_supported_currencies(self) -> list:
        return ['EGP']
    
    def _get_auth_token(self) -> str:
        """Get authentication token from Paymob"""
        url = f"{self.base_url}/auth/tokens"
        data = {"api_key": self.api_key}
        
        try:
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()['token']
        except Exception as e:
            raise Exception(f"Failed to get Paymob auth token: {str(e)}")
    
    def _create_order(self, auth_token: str, amount: Decimal, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create order in Paymob"""
        url = f"{self.base_url}/ecommerce/orders"
        
        data = {
            "auth_token": auth_token,
            "delivery_needed": "false",
            "amount_cents": self.format_amount_for_gateway(amount, 'EGP'),
            "currency": "EGP",
            "merchant_order_id": order_data.get('order_number', ''),
            "items": []
        }
        
        try:
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to create Paymob order: {str(e)}")
    
    def _create_payment_key(self, auth_token: str, order_id: int, amount: Decimal, order_data: Dict[str, Any]) -> str:
        """Create payment key for Paymob"""
        url = f"{self.base_url}/acceptance/payment_keys"
        
        billing_data = order_data.get('billing_address', {})
        
        data = {
            "auth_token": auth_token,
            "amount_cents": self.format_amount_for_gateway(amount, 'EGP'),
            "expiration": 3600,  # 1 hour
            "order_id": order_id,
            "billing_data": {
                "apartment": billing_data.get('apartment_number', 'N/A'),
                "email": order_data.get('customer_email', ''),
                "floor": billing_data.get('floor_number', 'N/A'),
                "first_name": order_data.get('customer_name', '').split(' ')[0] if order_data.get('customer_name') else 'N/A',
                "street": billing_data.get('street_address', 'N/A'),
                "building": billing_data.get('building_number', 'N/A'),
                "phone_number": order_data.get('customer_phone', ''),
                "shipping_method": "PKG",
                "postal_code": billing_data.get('postal_code', 'N/A'),
                "city": billing_data.get('city', 'N/A'),
                "country": "EG",
                "last_name": ' '.join(order_data.get('customer_name', '').split(' ')[1:]) if order_data.get('customer_name') else 'N/A',
                "state": billing_data.get('governorate', 'N/A')
            },
            "currency": "EGP",
            "integration_id": self.integration_id
        }
        
        try:
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()['token']
        except Exception as e:
            raise Exception(f"Failed to create Paymob payment key: {str(e)}")
    
    def create_payment_intent(self, amount: Decimal, currency: str, order_data: Dict[str, Any]) -> PaymentResult:
        """Create payment intent with Paymob"""
        if currency != 'EGP':
            return PaymentResult(success=False, error="Paymob only supports EGP currency")
        
        if not self.validate_amount(amount, currency):
            return PaymentResult(success=False, error="Invalid payment amount")
        
        try:
            # Step 1: Get auth token
            auth_token = self._get_auth_token()
            
            # Step 2: Create order
            paymob_order = self._create_order(auth_token, amount, order_data)
            
            # Step 3: Create payment key
            payment_key = self._create_payment_key(
                auth_token, 
                paymob_order['id'], 
                amount, 
                order_data
            )
            
            # Create payment URL
            payment_url = f"https://accept.paymob.com/api/acceptance/iframes/{self.integration_id}?payment_token={payment_key}"
            
            return PaymentResult(
                success=True,
                data={
                    'payment_intent_id': str(paymob_order['id']),
                    'payment_url': payment_url,
                    'payment_key': payment_key,
                    'paymob_order_id': paymob_order['id'],
                    'gateway_response': paymob_order
                }
            )
            
        except Exception as e:
            return self.handle_error(e, "create_payment_intent")
    
    def capture_payment(self, payment_intent_id: str, amount: Decimal = None) -> PaymentResult:
        """Capture payment (Paymob handles this automatically)"""
        # Paymob doesn't require manual capture, payment is captured automatically
        return PaymentResult(
            success=True,
            data={'message': 'Paymob handles payment capture automatically'}
        )
    
    def refund_payment(self, transaction_id: str, amount: Decimal, reason: str = None) -> PaymentResult:
        """Refund payment through Paymob"""
        try:
            auth_token = self._get_auth_token()
            url = f"{self.base_url}/acceptance/void_refund/refund"
            
            data = {
                "auth_token": auth_token,
                "transaction_id": transaction_id,
                "amount_cents": self.format_amount_for_gateway(amount, 'EGP')
            }
            
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                return PaymentResult(
                    success=True,
                    data={
                        'refund_id': result.get('id'),
                        'gateway_response': result
                    }
                )
            else:
                return PaymentResult(
                    success=False,
                    error=result.get('detail', 'Refund failed')
                )
                
        except Exception as e:
            return self.handle_error(e, "refund_payment")
    
    def get_payment_status(self, payment_intent_id: str) -> PaymentResult:
        """Get payment status from Paymob"""
        try:
            auth_token = self._get_auth_token()
            url = f"{self.base_url}/ecommerce/orders/{payment_intent_id}"
            
            headers = {"Authorization": f"Token {auth_token}"}
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            order_data = response.json()
            
            # Map Paymob status to our status
            paymob_status = order_data.get('closed', False)
            paid = order_data.get('paid_amount_cents', 0) > 0
            
            if paid and paymob_status:
                status = 'completed'
            elif paid:
                status = 'processing'
            else:
                status = 'pending'
            
            return PaymentResult(
                success=True,
                data={
                    'status': status,
                    'amount': self.parse_amount_from_gateway(order_data.get('amount_cents', 0), 'EGP'),
                    'paid_amount': self.parse_amount_from_gateway(order_data.get('paid_amount_cents', 0), 'EGP'),
                    'gateway_response': order_data
                }
            )
            
        except Exception as e:
            return self.handle_error(e, "get_payment_status")
    
    def handle_webhook(self, webhook_data: Dict[str, Any], headers: Dict[str, str] = None) -> PaymentResult:
        """Handle Paymob webhook"""
        try:
            # Extract relevant data
            transaction_id = webhook_data.get('id')
            order_id = webhook_data.get('order', {}).get('id')
            success = webhook_data.get('success', False)
            amount_cents = webhook_data.get('amount_cents', 0)
            
            # Determine status
            if success:
                status = 'completed'
            else:
                status = 'failed'
            
            return PaymentResult(
                success=True,
                data={
                    'transaction_id': str(order_id),  # Use order ID as transaction ID
                    'gateway_transaction_id': str(transaction_id),
                    'status': status,
                    'amount': self.parse_amount_from_gateway(amount_cents, 'EGP'),
                    'currency': 'EGP',
                    'gateway_response': webhook_data
                }
            )
            
        except Exception as e:
            return self.handle_error(e, "handle_webhook")
    
    def verify_webhook_signature(self, payload: str, signature: str, headers: Dict[str, str] = None) -> bool:
        """Verify Paymob webhook signature"""
        try:
            # Paymob uses HMAC SHA512 for webhook verification
            expected_signature = hmac.new(
                self.secret_key.encode(),
                payload.encode(),
                hashlib.sha512
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception:
            return False
    
    def get_payment_url(self, payment_intent_id: str) -> str:
        """Get payment URL for Paymob iframe"""
        # This would typically be constructed with the payment key
        # For now, return a placeholder
        return f"https://accept.paymob.com/api/acceptance/iframes/{self.integration_id}"
