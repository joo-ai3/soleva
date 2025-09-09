from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'flash-sales', views.FlashSaleViewSet, basename='flash-sales')
router.register(r'special-offers', views.SpecialOfferViewSet, basename='special-offers')

urlpatterns = [
    path('', include(router.urls)),
    
    # Offer calculation endpoints
    path('calculate/', views.calculate_offers, name='calculate-offers'),
    path('check-product/', views.check_product_offers, name='check-product-offers'),
    path('record-usage/', views.record_offer_usage, name='record-offer-usage'),
    
    # Admin endpoints
    path('flash-sales/<uuid:pk>/activate/', views.activate_flash_sale, name='activate-flash-sale'),
    path('special-offers/<uuid:pk>/activate/', views.activate_special_offer, name='activate-special-offer'),
    path('analytics/', views.offer_analytics, name='offer-analytics'),
]
