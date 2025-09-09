"""
Accounting System API Views
Real-time financial data and document generation
"""

from decimal import Decimal
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from django.core.files.base import ContentFile
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from .models import (
    SalesRecord, BusinessExpense, InventoryTransaction, ProductCost,
    Invoice, ShippingLabel, FinancialReport, ExpenseCategory
)
from .serializers import (
    SalesRecordSerializer, BusinessExpenseSerializer, InventoryTransactionSerializer,
    ProductCostSerializer, InvoiceSerializer, ShippingLabelSerializer,
    FinancialReportSerializer, ExpenseCategorySerializer
)
from .services import (
    invoice_generator, label_generator, report_service, calculation_service
)
from orders.models import Order


class SalesRecordViewSet(viewsets.ModelViewSet):
    """Sales records management"""
    queryset = SalesRecord.objects.all()
    serializer_class = SalesRecordSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sale_date', 'is_return']
    ordering = ['-sale_date']
    
    @action(detail=False, methods=['get'])
    def daily_sales(self, request):
        """Get today's sales summary"""
        today = timezone.now().date()
        today_sales = self.queryset.filter(sale_date__date=today, is_return=False)
        
        summary = today_sales.aggregate(
            total_revenue=Sum('gross_revenue'),
            total_profit=Sum('net_profit'),
            total_orders=Count('id')
        )
        
        return Response({
            'date': today,
            'total_revenue': summary['total_revenue'] or Decimal('0.00'),
            'total_profit': summary['total_profit'] or Decimal('0.00'),
            'total_orders': summary['total_orders'] or 0,
            'average_order_value': (summary['total_revenue'] / summary['total_orders']) if summary['total_orders'] > 0 else Decimal('0.00')
        })
    
    @action(detail=False, methods=['get'])
    def period_analysis(self, request):
        """Analyze sales for custom period"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date parameters required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        analysis = calculation_service.calculate_period_profit(start_date, end_date)
        top_products = calculation_service.get_top_selling_products(start_date, end_date)
        
        return Response({
            'period': {'start_date': start_date, 'end_date': end_date},
            'financial_summary': analysis,
            'top_products': top_products
        })


class BusinessExpenseViewSet(viewsets.ModelViewSet):
    """Business expenses management"""
    queryset = BusinessExpense.objects.all()
    serializer_class = BusinessExpenseSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['expense_type', 'category', 'expense_date']
    ordering = ['-expense_date']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def monthly_expenses(self, request):
        """Get monthly expense breakdown"""
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month', timezone.now().month)
        
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return Response(
                {'error': 'Invalid year or month'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        expenses = self.queryset.filter(
            expense_date__year=year,
            expense_date__month=month
        )
        
        # Group by expense type
        by_type = expenses.values('expense_type').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Group by category
        by_category = expenses.values('category__name_en').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        return Response({
            'period': {'year': year, 'month': month},
            'total_expenses': total_expenses,
            'by_type': by_type,
            'by_category': by_category
        })


class InventoryTransactionViewSet(viewsets.ModelViewSet):
    """Inventory transactions management"""
    queryset = InventoryTransaction.objects.all()
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'transaction_type', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def low_stock_alert(self, request):
        """Get products with low stock"""
        from products.models import Product
        
        LOW_STOCK_THRESHOLD = int(request.query_params.get('threshold', 10))
        
        low_stock_products = Product.objects.filter(
            stock_quantity__lte=LOW_STOCK_THRESHOLD,
            is_active=True
        ).values(
            'id', 'name', 'stock_quantity', 'sku'
        )
        
        return Response({
            'threshold': LOW_STOCK_THRESHOLD,
            'products': list(low_stock_products)
        })
    
    @action(detail=False, methods=['get'])
    def inventory_valuation(self, request):
        """Get current inventory valuation"""
        valuation = calculation_service.get_inventory_valuation()
        return Response(valuation)


class ProductCostViewSet(viewsets.ModelViewSet):
    """Product cost management"""
    queryset = ProductCost.objects.all()
    serializer_class = ProductCostSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product']
    
    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class InvoiceViewSet(viewsets.ModelViewSet):
    """Invoice management and generation"""
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'invoice_type', 'issue_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter invoices based on user permissions"""
        if self.request.user.is_staff:
            return self.queryset
        else:
            # Regular users can only see their own invoices
            return self.queryset.filter(order__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        """Generate PDF for invoice"""
        invoice = self.get_object()
        
        try:
            pdf_buffer = invoice_generator.generate_invoice_pdf(invoice)
            
            # Save PDF to invoice
            invoice.pdf_file.save(
                f'invoice_{invoice.invoice_number}.pdf',
                ContentFile(pdf_buffer.getvalue()),
                save=True
            )
            
            return Response({
                'message': 'PDF generated successfully',
                'pdf_url': invoice.pdf_file.url if invoice.pdf_file else None
            })
            
        except Exception as e:
            return Response(
                {'error': f'PDF generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Download invoice PDF"""
        invoice = self.get_object()
        
        if not invoice.pdf_file:
            # Generate PDF if it doesn't exist
            try:
                pdf_buffer = invoice_generator.generate_invoice_pdf(invoice)
                invoice.pdf_file.save(
                    f'invoice_{invoice.invoice_number}.pdf',
                    ContentFile(pdf_buffer.getvalue()),
                    save=True
                )
            except Exception as e:
                return Response(
                    {'error': 'PDF generation failed'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        response = HttpResponse(
            invoice.pdf_file.read(),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        return response


class ShippingLabelViewSet(viewsets.ModelViewSet):
    """Shipping label management"""
    queryset = ShippingLabel.objects.all()
    serializer_class = ShippingLabelSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['governorate', 'city', 'shipping_method']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        """Generate PDF for shipping label"""
        label = self.get_object()
        
        try:
            pdf_buffer = label_generator.generate_shipping_label_pdf(label)
            
            # Save PDF to label
            label.pdf_file.save(
                f'shipping_label_{label.label_number}.pdf',
                ContentFile(pdf_buffer.getvalue()),
                save=True
            )
            
            return Response({
                'message': 'Shipping label PDF generated successfully',
                'pdf_url': label.pdf_file.url if label.pdf_file else None
            })
            
        except Exception as e:
            return Response(
                {'error': f'PDF generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Download shipping label PDF"""
        label = self.get_object()
        
        if not label.pdf_file:
            # Generate PDF if it doesn't exist
            try:
                pdf_buffer = label_generator.generate_shipping_label_pdf(label)
                label.pdf_file.save(
                    f'shipping_label_{label.label_number}.pdf',
                    ContentFile(pdf_buffer.getvalue()),
                    save=True
                )
            except Exception as e:
                return Response(
                    {'error': 'PDF generation failed'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        response = HttpResponse(
            label.pdf_file.read(),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="shipping_label_{label.label_number}.pdf"'
        return response


class FinancialReportViewSet(viewsets.ModelViewSet):
    """Financial reports management"""
    queryset = FinancialReport.objects.all()
    serializer_class = FinancialReportSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_type', 'start_date', 'end_date']
    ordering = ['-generated_at']
    
    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """Generate new financial report"""
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        report_type = request.data.get('report_type', 'custom')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                report = report_service.generate_period_report(
                    start_date, end_date, report_type
                )
                
            serializer = self.get_serializer(report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Report generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Download report PDF"""
        report = self.get_object()
        
        if not report.pdf_file:
            return Response(
                {'error': 'PDF file not available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = HttpResponse(
            report.pdf_file.read(),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="financial_report_{report.start_date}_{report.end_date}.pdf"'
        return response
    
    @action(detail=True, methods=['get'])
    def download_excel(self, request, pk=None):
        """Download report Excel"""
        report = self.get_object()
        
        if not report.excel_file:
            return Response(
                {'error': 'Excel file not available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = HttpResponse(
            report.excel_file.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="financial_report_{report.start_date}_{report.end_date}.xlsx"'
        return response


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    """Expense categories management"""
    queryset = ExpenseCategory.objects.filter(is_active=True)
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


# Dashboard API views
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def dashboard_overview(request):
    """Get dashboard overview data"""
    today = timezone.now().date()
    
    # Today's metrics
    today_sales = SalesRecord.objects.filter(sale_date__date=today, is_return=False)
    today_revenue = today_sales.aggregate(Sum('gross_revenue'))['gross_revenue__sum'] or Decimal('0.00')
    today_profit = today_sales.aggregate(Sum('net_profit'))['net_profit__sum'] or Decimal('0.00')
    today_orders = today_sales.count()
    
    # This month's metrics
    month_start = today.replace(day=1)
    month_sales = SalesRecord.objects.filter(sale_date__date__gte=month_start, is_return=False)
    month_revenue = month_sales.aggregate(Sum('gross_revenue'))['gross_revenue__sum'] or Decimal('0.00')
    month_profit = month_sales.aggregate(Sum('net_profit'))['net_profit__sum'] or Decimal('0.00')
    month_orders = month_sales.count()
    
    # Low stock alerts
    from products.models import Product
    low_stock_count = Product.objects.filter(stock_quantity__lte=10, is_active=True).count()
    
    # Recent transactions
    recent_transactions = InventoryTransaction.objects.select_related('product')[:5]
    
    return Response({
        'today': {
            'revenue': today_revenue,
            'profit': today_profit,
            'orders': today_orders
        },
        'month': {
            'revenue': month_revenue,
            'profit': month_profit,
            'orders': month_orders
        },
        'alerts': {
            'low_stock_count': low_stock_count
        },
        'recent_transactions': InventoryTransactionSerializer(recent_transactions, many=True).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def sales_chart_data(request):
    """Get sales chart data for dashboard"""
    days = int(request.query_params.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Daily sales data
    daily_sales = SalesRecord.objects.filter(
        sale_date__date__range=[start_date, end_date],
        is_return=False
    ).extra(
        select={'day': 'date(sale_date)'}
    ).values('day').annotate(
        revenue=Sum('gross_revenue'),
        profit=Sum('net_profit'),
        orders=Count('id')
    ).order_by('day')
    
    return Response({
        'period': {'start_date': start_date, 'end_date': end_date, 'days': days},
        'daily_data': list(daily_sales)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def bulk_generate_documents(request):
    """Bulk generate invoices and shipping labels for orders"""
    order_ids = request.data.get('order_ids', [])
    document_types = request.data.get('document_types', ['invoice', 'shipping_label'])
    
    if not order_ids:
        return Response(
            {'error': 'order_ids required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    results = {'invoices': [], 'shipping_labels': [], 'errors': []}
    
    for order_id in order_ids:
        try:
            order = Order.objects.get(id=order_id)
            
            # Generate invoice
            if 'invoice' in document_types:
                if not hasattr(order, 'invoices') or not order.invoices.exists():
                    invoice = Invoice.objects.create(
                        order=order,
                        invoice_number=Invoice().generate_invoice_number(),
                        issue_date=order.created_at.date(),
                        due_date=order.created_at.date(),
                        subtotal=order.subtotal or order.total_amount,
                        shipping_amount=order.shipping_cost or Decimal('0.00'),
                        discount_amount=order.discount_amount or Decimal('0.00'),
                        total_amount=order.total_amount,
                        status='sent',
                        created_by=request.user
                    )
                    results['invoices'].append(invoice.id)
            
            # Generate shipping label
            if 'shipping_label' in document_types:
                if not hasattr(order, 'shipping_label'):
                    shipping_label = ShippingLabel.objects.create(
                        order=order,
                        label_number=ShippingLabel().generate_label_number(),
                        recipient_name=f"{order.shipping_address.get('first_name', '')} {order.shipping_address.get('last_name', '')}".strip(),
                        recipient_phone=order.shipping_address.get('phone', ''),
                        delivery_address=f"{order.shipping_address.get('address_line_1', '')}, {order.shipping_address.get('address_line_2', '')}".strip(', '),
                        governorate=order.shipping_address.get('governorate', ''),
                        city=order.shipping_address.get('city', ''),
                        shipping_cost=order.shipping_cost or Decimal('0.00'),
                        cash_on_delivery=order.total_amount if order.payment_method == 'cash_on_delivery' else Decimal('0.00'),
                        shipping_method=order.shipping_method or 'Standard Shipping',
                        created_by=request.user
                    )
                    results['shipping_labels'].append(shipping_label.id)
                    
        except Order.DoesNotExist:
            results['errors'].append(f'Order {order_id} not found')
        except Exception as e:
            results['errors'].append(f'Error processing order {order_id}: {str(e)}')
    
    return Response(results)
