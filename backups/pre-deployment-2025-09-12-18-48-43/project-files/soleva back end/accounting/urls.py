"""
Accounting System URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'sales-records', views.SalesRecordViewSet, basename='sales-records')
router.register(r'expenses', views.BusinessExpenseViewSet, basename='expenses')
router.register(r'inventory-transactions', views.InventoryTransactionViewSet, basename='inventory-transactions')
router.register(r'product-costs', views.ProductCostViewSet, basename='product-costs')
router.register(r'invoices', views.InvoiceViewSet, basename='invoices')
router.register(r'shipping-labels', views.ShippingLabelViewSet, basename='shipping-labels')
router.register(r'reports', views.FinancialReportViewSet, basename='reports')
router.register(r'expense-categories', views.ExpenseCategoryViewSet, basename='expense-categories')

app_name = 'accounting'

urlpatterns = [
    # Dashboard endpoints
    path('dashboard/overview/', views.dashboard_overview, name='dashboard-overview'),
    path('dashboard/sales-chart/', views.sales_chart_data, name='sales-chart-data'),
    
    # Bulk operations
    path('bulk/generate-documents/', views.bulk_generate_documents, name='bulk-generate-documents'),
    
    # Include router URLs
    path('', include(router.urls)),
]
