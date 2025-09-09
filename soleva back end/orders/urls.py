from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'orders'

# Create router for viewsets
router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='orders')
router.register(r'payment-proofs', views.PaymentProofViewSet, basename='payment-proofs')

urlpatterns = [
    # Order statistics
    path('stats/', views.order_stats, name='order_stats'),
    
    # Public order tracking
    path('track/', views.track_order, name='track_order'),
    
    # Payment proof upload
    path('orders/<int:order_id>/upload-payment-proof/', views.upload_payment_proof, name='upload_payment_proof'),
    
    # Include router URLs
    path('', include(router.urls)),
]
