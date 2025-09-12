"""
Accounting System Serializers
"""

from rest_framework import serializers
from decimal import Decimal
from .models import (
    SalesRecord, BusinessExpense, InventoryTransaction, ProductCost,
    Invoice, ShippingLabel, FinancialReport, ExpenseCategory, Currency
)
from orders.models import Order
from products.models import Product


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class ProductCostSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.full_name', read_only=True)
    
    class Meta:
        model = ProductCost
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'production_cost', 'packaging_cost', 'total_cost',
            'last_updated', 'updated_by', 'updated_by_name', 'notes'
        ]
        read_only_fields = ['last_updated', 'updated_by']
    
    def validate_production_cost(self, value):
        if value < Decimal('0.00'):
            raise serializers.ValidationError("Production cost cannot be negative")
        return value
    
    def validate_packaging_cost(self, value):
        if value < Decimal('0.00'):
            raise serializers.ValidationError("Packaging cost cannot be negative")
        return value


class InventoryTransactionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'product', 'product_name', 'variant', 'variant_name',
            'transaction_type', 'transaction_type_display', 'quantity',
            'previous_stock', 'new_stock', 'unit_cost', 'total_cost',
            'order', 'order_number', 'reference_number', 'notes',
            'created_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = ['created_at', 'created_by']
    
    def validate_quantity(self, value):
        if value == 0:
            raise serializers.ValidationError("Quantity cannot be zero")
        return value


class SalesRecordSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    customer_name = serializers.SerializerMethodField()
    gross_profit = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    net_profit = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    profit_margin_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = SalesRecord
        fields = [
            'id', 'order', 'order_number', 'customer_name',
            'gross_revenue', 'total_cost_of_goods', 'shipping_cost',
            'packaging_cost', 'payment_gateway_fee', 'discount_amount',
            'coupon_discount', 'gross_profit', 'net_profit',
            'profit_margin_percentage', 'sale_date', 'is_return',
            'return_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['gross_profit', 'net_profit', 'profit_margin_percentage', 'created_at', 'updated_at']
    
    def get_customer_name(self, obj):
        return f"{obj.order.user.first_name} {obj.order.user.last_name}".strip()
    
    def validate_gross_revenue(self, value):
        if value < Decimal('0.00'):
            raise serializers.ValidationError("Gross revenue cannot be negative")
        return value


class ExpenseCategorySerializer(serializers.ModelSerializer):
    expenses_count = serializers.SerializerMethodField()
    total_expenses = serializers.SerializerMethodField()
    
    class Meta:
        model = ExpenseCategory
        fields = [
            'id', 'name_en', 'name_ar', 'description',
            'is_active', 'created_at', 'expenses_count', 'total_expenses'
        ]
        read_only_fields = ['created_at']
    
    def get_expenses_count(self, obj):
        return obj.expenses.count()
    
    def get_total_expenses(self, obj):
        total = obj.expenses.aggregate(total=serializers.models.Sum('amount'))['total']
        return total or Decimal('0.00')


class BusinessExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name_en', read_only=True)
    expense_type_display = serializers.CharField(source='get_expense_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    recurring_frequency_display = serializers.CharField(source='get_recurring_frequency_display', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = BusinessExpense
        fields = [
            'id', 'category', 'category_name', 'expense_type', 'expense_type_display',
            'title', 'description', 'amount', 'expense_date', 'payment_method',
            'receipt_number', 'supplier_vendor', 'is_recurring',
            'recurring_frequency', 'recurring_frequency_display', 'tags',
            'receipt_file', 'file_size_mb', 'created_at', 'updated_at',
            'created_by', 'created_by_name'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']
    
    def get_file_size_mb(self, obj):
        if obj.receipt_file:
            return round(obj.receipt_file.size / (1024 * 1024), 2)
        return None
    
    def validate_amount(self, value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Amount must be greater than zero")
        return value


class InvoiceSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    customer_name = serializers.SerializerMethodField()
    customer_email = serializers.CharField(source='order.user.email', read_only=True)
    invoice_type_display = serializers.CharField(source='get_invoice_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'order', 'order_number',
            'customer_name', 'customer_email', 'invoice_type',
            'invoice_type_display', 'status', 'status_display',
            'issue_date', 'due_date', 'subtotal', 'tax_amount',
            'shipping_amount', 'discount_amount', 'total_amount',
            'notes', 'terms_conditions', 'pdf_file', 'pdf_url',
            'email_sent', 'email_sent_at', 'created_at', 'updated_at',
            'created_by', 'created_by_name'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'email_sent_at']
    
    def get_customer_name(self, obj):
        return f"{obj.order.user.first_name} {obj.order.user.last_name}".strip()
    
    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None
    
    def validate_total_amount(self, value):
        if value < Decimal('0.00'):
            raise serializers.ValidationError("Total amount cannot be negative")
        return value


class ShippingLabelSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    pdf_url = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()
    
    class Meta:
        model = ShippingLabel
        fields = [
            'id', 'order', 'order_number', 'label_number',
            'recipient_name', 'recipient_phone', 'delivery_address',
            'full_address', 'governorate', 'city', 'postal_code',
            'shipping_cost', 'cash_on_delivery', 'shipping_method',
            'tracking_number', 'special_instructions', 'pdf_file',
            'pdf_url', 'created_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = ['created_at', 'created_by']
    
    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None
    
    def get_full_address(self, obj):
        parts = [obj.delivery_address, obj.city, obj.governorate]
        if obj.postal_code:
            parts.append(obj.postal_code)
        return ', '.join(filter(None, parts))
    
    def validate_shipping_cost(self, value):
        if value < Decimal('0.00'):
            raise serializers.ValidationError("Shipping cost cannot be negative")
        return value
    
    def validate_cash_on_delivery(self, value):
        if value < Decimal('0.00'):
            raise serializers.ValidationError("COD amount cannot be negative")
        return value


class FinancialReportSerializer(serializers.ModelSerializer):
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    report_format_display = serializers.CharField(source='get_report_format_display', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.full_name', read_only=True)
    pdf_url = serializers.SerializerMethodField()
    excel_url = serializers.SerializerMethodField()
    period_days = serializers.SerializerMethodField()
    
    class Meta:
        model = FinancialReport
        fields = [
            'id', 'report_type', 'report_type_display',
            'report_format', 'report_format_display',
            'start_date', 'end_date', 'period_days',
            'total_revenue', 'total_costs', 'total_expenses',
            'gross_profit', 'net_profit', 'profit_margin',
            'total_orders', 'average_order_value',
            'pdf_file', 'pdf_url', 'excel_file', 'excel_url',
            'generated_at', 'generated_by', 'generated_by_name'
        ]
        read_only_fields = ['generated_at', 'generated_by']
    
    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None
    
    def get_excel_url(self, obj):
        if obj.excel_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.excel_file.url)
            return obj.excel_file.url
        return None
    
    def get_period_days(self, obj):
        return (obj.end_date - obj.start_date).days + 1


# Dashboard specific serializers
class DashboardSummarySerializer(serializers.Serializer):
    """Dashboard summary data serializer"""
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_profit = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_orders = serializers.IntegerField()
    profit_margin = serializers.DecimalField(max_digits=5, decimal_places=2)
    growth_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)


class TopProductSerializer(serializers.Serializer):
    """Top selling products serializer"""
    product_name = serializers.CharField()
    total_quantity = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)


class SalesChartDataSerializer(serializers.Serializer):
    """Sales chart data serializer"""
    date = serializers.DateField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    orders = serializers.IntegerField()


class ExpenseChartDataSerializer(serializers.Serializer):
    """Expense chart data serializer"""
    expense_type = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2)


class InventoryValueSerializer(serializers.Serializer):
    """Inventory valuation serializer"""
    product_name = serializers.CharField()
    stock_quantity = serializers.IntegerField()
    unit_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2)


# Bulk operations serializers
class BulkDocumentGenerationSerializer(serializers.Serializer):
    """Bulk document generation request serializer"""
    order_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=100
    )
    document_types = serializers.ListField(
        child=serializers.ChoiceField(choices=['invoice', 'shipping_label']),
        min_length=1
    )


class BulkDocumentResponseSerializer(serializers.Serializer):
    """Bulk document generation response serializer"""
    invoices = serializers.ListField(child=serializers.UUIDField())
    shipping_labels = serializers.ListField(child=serializers.UUIDField())
    errors = serializers.ListField(child=serializers.CharField())


# Period analysis serializers
class PeriodAnalysisRequestSerializer(serializers.Serializer):
    """Period analysis request serializer"""
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date must be before end date")
        return data


class PeriodAnalysisResponseSerializer(serializers.Serializer):
    """Period analysis response serializer"""
    period = serializers.DictField()
    financial_summary = serializers.DictField()
    top_products = TopProductSerializer(many=True)
    sales_trend = SalesChartDataSerializer(many=True, required=False)
