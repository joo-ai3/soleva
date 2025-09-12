"""
URL configuration for soleva_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for load balancer"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'soleva-backend',
        'version': '1.0.0'
    })

@require_http_methods(["GET"])
def api_root(request):
    """API root endpoint"""
    return JsonResponse({
        'message': 'Soleva E-commerce API',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'auth': '/api/auth/',
            'products': '/api/products/',
            'orders': '/api/orders/',
            'cart': '/api/cart/',
            'users': '/api/users/',
            'health': '/api/health/'
        }
    })

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Health Check
    path('api/health/', health_check, name='health_check'),
    path('health/', health_check, name='health_check_alt'),
    
    # API Root
    path('api/', api_root, name='api_root'),
    
    # API Endpoints
    # Admin Panel API
    path('api/admin/', include('admin_panel.urls')),
    path('api/auth/', include('users.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/cart/', include('cart.urls')),
    path('api/coupons/', include('coupons.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/accounting/', include('accounting.urls')),
    path('api/shipping/', include('shipping.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/tracking/', include('tracking.urls')),
    path('api/offers/', include('offers.urls')),
    path('api/otp/', include('otp.urls')),
    path('api/website/', include('website_management.urls')),
]

# Media files serving (development only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)