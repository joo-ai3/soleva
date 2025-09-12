from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    
    # Statistics
    path('stats/overview/', views.overview_stats, name='overview_stats'),
    path('stats/sales/', views.sales_stats, name='sales_stats'),
    path('stats/customers/', views.customer_stats, name='customer_stats'),
    path('stats/products/', views.product_stats, name='product_stats'),
    
    # Reports
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/customers/', views.customer_report, name='customer_report'),
    path('reports/inventory/', views.inventory_report, name='inventory_report'),
    
    # Quick actions
    path('actions/low-stock/', views.low_stock_products, name='low_stock_products'),
    path('actions/pending-orders/', views.pending_orders, name='pending_orders'),
    path('actions/recent-customers/', views.recent_customers, name='recent_customers'),
]
