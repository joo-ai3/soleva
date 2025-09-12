from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'products'

# Create router for viewsets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='categories')
router.register(r'brands', views.BrandViewSet, basename='brands')
router.register(r'products', views.ProductViewSet, basename='products')
router.register(r'attributes', views.ProductAttributeViewSet, basename='attributes')

urlpatterns = [
    # Product statistics
    path('stats/', views.product_stats, name='product_stats'),
    
    # Search suggestions
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    
    # Include router URLs
    path('', include(router.urls)),
]
