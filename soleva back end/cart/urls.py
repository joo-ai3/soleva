from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cart'

# Create router for viewsets
router = DefaultRouter()
router.register(r'items', views.CartItemViewSet, basename='cart-items')
router.register(r'saved', views.SavedForLaterViewSet, basename='saved-for-later')

urlpatterns = [
    # Cart management
    path('', views.CartView.as_view(), name='cart'),
    path('add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('summary/', views.cart_summary, name='cart_summary'),
    
    # Coupon management
    path('coupon/apply/', views.apply_coupon, name='apply_coupon'),
    
    # Include router URLs
    path('', include(router.urls)),
]
