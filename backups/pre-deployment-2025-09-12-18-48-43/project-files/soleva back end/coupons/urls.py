from django.urls import path
from . import views

app_name = 'coupons'

urlpatterns = [
    # Coupon validation and usage
    path('validate/', views.validate_coupon, name='validate_coupon'),
    path('apply/', views.apply_coupon, name='apply_coupon'),
    
    # Coupon management (admin)
    path('', views.CouponListView.as_view(), name='coupon_list'),
    path('create/', views.CouponCreateView.as_view(), name='coupon_create'),
    path('<int:pk>/', views.CouponDetailView.as_view(), name='coupon_detail'),
    path('<int:pk>/update/', views.CouponUpdateView.as_view(), name='coupon_update'),
    path('<int:pk>/delete/', views.CouponDeleteView.as_view(), name='coupon_delete'),
    
    # Coupon usage statistics
    path('stats/', views.coupon_stats, name='coupon_stats'),
    path('<int:pk>/usage/', views.coupon_usage, name='coupon_usage'),
]
