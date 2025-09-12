"""
Base payment gateway class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal


class PaymentResult:
    """Payment operation result"""
    
    def __init__(self, success: bool, data: Dict[str, Any] = None, error: str = None):
        self.success = success
        self.data = data or {}
        self.error = error
    
    @property
    def is_successful(self) -> bool:
        return self.success
    
    @property
    def is_failed(self) -> bool:
        return not self.success


class BasePaymentGateway(ABC):
    """Base class for payment gateways"""
    
    def __init__(self):
        self.gateway_name = self.get_gateway_name()
    
    @abstractmethod
    def get_gateway_name(self) -> str:
        """Get gateway name"""
        pass
    
    @abstractmethod
    def create_payment_intent(self, amount: Decimal, currency: str, order_data: Dict[str, Any]) -> PaymentResult:
        """Create payment intent/session"""
        pass
    
    @abstractmethod
    def capture_payment(self, payment_intent_id: str, amount: Decimal = None) -> PaymentResult:
        """Capture payment"""
        pass
    
    @abstractmethod
    def refund_payment(self, transaction_id: str, amount: Decimal, reason: str = None) -> PaymentResult:
        """Refund payment"""
        pass
    
    @abstractmethod
    def get_payment_status(self, payment_intent_id: str) -> PaymentResult:
        """Get payment status"""
        pass
    
    @abstractmethod
    def handle_webhook(self, webhook_data: Dict[str, Any], headers: Dict[str, str] = None) -> PaymentResult:
        """Handle webhook from payment gateway"""
        pass
    
    @abstractmethod
    def verify_webhook_signature(self, payload: str, signature: str, headers: Dict[str, str] = None) -> bool:
        """Verify webhook signature"""
        pass
    
    def get_supported_currencies(self) -> list:
        """Get supported currencies"""
        return ['EGP', 'USD', 'EUR']
    
    def get_minimum_amount(self, currency: str = 'EGP') -> Decimal:
        """Get minimum payment amount"""
        minimums = {
            'EGP': Decimal('1.00'),
            'USD': Decimal('0.50'),
            'EUR': Decimal('0.50'),
        }
        return minimums.get(currency, Decimal('1.00'))
    
    def get_maximum_amount(self, currency: str = 'EGP') -> Optional[Decimal]:
        """Get maximum payment amount"""
        maximums = {
            'EGP': Decimal('100000.00'),  # 100K EGP
            'USD': Decimal('10000.00'),   # 10K USD
            'EUR': Decimal('10000.00'),   # 10K EUR
        }
        return maximums.get(currency)
    
    def validate_amount(self, amount: Decimal, currency: str = 'EGP') -> bool:
        """Validate payment amount"""
        min_amount = self.get_minimum_amount(currency)
        max_amount = self.get_maximum_amount(currency)
        
        if amount < min_amount:
            return False
        
        if max_amount and amount > max_amount:
            return False
        
        return True
    
    def format_amount_for_gateway(self, amount: Decimal, currency: str = 'EGP') -> int:
        """Format amount for gateway (usually in smallest currency unit)"""
        # Most gateways expect amount in cents/piastres
        if currency in ['EGP', 'USD', 'EUR']:
            return int(amount * 100)
        return int(amount)
    
    def parse_amount_from_gateway(self, amount: int, currency: str = 'EGP') -> Decimal:
        """Parse amount from gateway response"""
        if currency in ['EGP', 'USD', 'EUR']:
            return Decimal(str(amount / 100))
        return Decimal(str(amount))
    
    def get_payment_url(self, payment_intent_id: str) -> Optional[str]:
        """Get payment URL for redirect"""
        return None
    
    def is_webhook_valid(self, webhook_data: Dict[str, Any]) -> bool:
        """Basic webhook validation"""
        return True
    
    def extract_transaction_id(self, webhook_data: Dict[str, Any]) -> Optional[str]:
        """Extract transaction ID from webhook data"""
        return webhook_data.get('transaction_id')
    
    def extract_gateway_transaction_id(self, webhook_data: Dict[str, Any]) -> Optional[str]:
        """Extract gateway transaction ID from webhook data"""
        return webhook_data.get('gateway_transaction_id')
    
    def get_failure_reason(self, response_data: Dict[str, Any]) -> str:
        """Extract failure reason from gateway response"""
        return response_data.get('error', 'Unknown error')
    
    def log_gateway_request(self, endpoint: str, data: Dict[str, Any], response: Dict[str, Any]):
        """Log gateway request/response for debugging"""
        # In production, you might want to use proper logging
        # and be careful not to log sensitive data
        pass
    
    def handle_error(self, error: Exception, context: str = None) -> PaymentResult:
        """Handle gateway errors"""
        error_message = str(error)
        if context:
            error_message = f"{context}: {error_message}"
        
        return PaymentResult(success=False, error=error_message)
