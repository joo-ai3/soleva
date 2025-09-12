"""
Payment gateways integration
"""

from .base import BasePaymentGateway
from .paymob import PaymobGateway
from .stripe_gateway import StripeGateway
from .cash_on_delivery import CashOnDeliveryGateway

# Gateway registry
PAYMENT_GATEWAYS = {
    'paymob': PaymobGateway,
    'stripe': StripeGateway,
    'cash_on_delivery': CashOnDeliveryGateway,
}


def get_gateway(gateway_name):
    """Get payment gateway instance"""
    gateway_class = PAYMENT_GATEWAYS.get(gateway_name)
    if not gateway_class:
        raise ValueError(f"Unknown payment gateway: {gateway_name}")
    
    return gateway_class()
