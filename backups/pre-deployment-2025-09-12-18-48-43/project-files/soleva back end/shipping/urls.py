from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'governorates', views.GovernorateViewSet, basename='governorates')
router.register(r'cities', views.CityViewSet, basename='cities')
router.register(r'methods', views.ShippingMethodViewSet, basename='shipping-methods')

urlpatterns = [
    path('', include(router.urls)),
    path('calculate/', views.calculate_shipping, name='calculate-shipping'),
    path('validate-address/', views.validate_address, name='validate-address'),
    path('estimate-delivery/', views.estimate_delivery, name='estimate-delivery'),
    path('search/', views.search_locations, name='search-locations'),
    path('zones/', views.shipping_zones, name='shipping-zones'),
    path('stats/', views.shipping_stats, name='shipping-stats'),
]