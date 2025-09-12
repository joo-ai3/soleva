"""
Accounting System Django Admin Configuration
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from decimal import Decimal
from .models import (
    SalesRecord, BusinessExpense, InventoryTransaction, ProductCost,
    Invoice, ShippingLabel, FinancialReport, ExpenseCategory, Currency
)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(ProductCost)
class ProductCostAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'production_cost', 'packaging_cost', 
        'total_cost_display', 'last_updated', 'updated_by'
    ]
    list_filter = ['last_updated', 'updated_by']
    search_fields = ['product__name', 'product__sku']
    readonly_fields = ['last_updated']
    
    def total_cost_display(self, obj):
        return f"{obj.total_cost:.2f} EGP"
    total_cost_display.short_description = 'Total Cost'
    total_cost_display.admin_order_field = 'total_cost'
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'product', 'transaction_type', 'quantity',
        'previous_stock', 'new_stock', 'total_cost_display',
        'created_at', 'created_by'
    ]
    list_filter = [
        'transaction_type', 'created_at', 'created_by'
    ]
    search_fields = [
        'product__name', 'reference_number', 'order__order_number'
    ]
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    def total_cost_display(self, obj):
        if obj.total_cost:
            return f"{obj.total_cost:.2f} EGP"
        return "-"
    total_cost_display.short_description = 'Total Cost'
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SalesRecord)
class SalesRecordAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'gross_revenue_display', 'gross_profit_display',
        'net_profit_display', 'profit_margin_display', 'sale_date', 'is_return'
    ]
    list_filter = [
        'is_return', 'sale_date', 'order__payment_status'
    ]
    search_fields = [
        'order__order_number', 'order__user__email',
        'order__user__first_name', 'order__user__last_name'
    ]
    readonly_fields = [
        'gross_profit', 'net_profit', 'profit_margin_percentage',
        'created_at', 'updated_at'
    ]
    date_hierarchy = 'sale_date'
    
    def gross_revenue_display(self, obj):
        return f"{obj.gross_revenue:.2f} EGP"
    gross_revenue_display.short_description = 'Revenue'
    gross_revenue_display.admin_order_field = 'gross_revenue'
    
    def gross_profit_display(self, obj):
        color = 'green' if obj.gross_profit > 0 else 'red'
        return format_html(
            '<span style="color: {};">{:.2f} EGP</span>',
            color, obj.gross_profit
        )
    gross_profit_display.short_description = 'Gross Profit'
    gross_profit_display.admin_order_field = 'gross_profit'
    
    def net_profit_display(self, obj):
        color = 'green' if obj.net_profit > 0 else 'red'
        return format_html(
            '<span style="color: {};">{:.2f} EGP</span>',
            color, obj.net_profit
        )
    net_profit_display.short_description = 'Net Profit'
    net_profit_display.admin_order_field = 'net_profit'
    
    def profit_margin_display(self, obj):
        if obj.profit_margin_percentage:
            color = 'green' if obj.profit_margin_percentage > 0 else 'red'
            return format_html(
                '<span style="color: {};">{:.2f}%</span>',
                color, obj.profit_margin_percentage
            )
        return "-"
    profit_margin_display.short_description = 'Margin %'
    profit_margin_display.admin_order_field = 'profit_margin_percentage'


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name_en', 'name_ar']


@admin.register(BusinessExpense)
class BusinessExpenseAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'expense_type', 'amount_display',
        'expense_date', 'is_recurring', 'created_by'
    ]
    list_filter = [
        'expense_type', 'category', 'is_recurring',
        'expense_date', 'created_by'
    ]
    search_fields = [
        'title', 'description', 'supplier_vendor', 'receipt_number'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'expense_date'
    
    def amount_display(self, obj):
        return f"{obj.amount:.2f} EGP"
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'order', 'invoice_type', 'status',
        'total_amount_display', 'issue_date', 'email_sent'
    ]
    list_filter = [
        'invoice_type', 'status', 'issue_date', 'email_sent'
    ]
    search_fields = [
        'invoice_number', 'order__order_number',
        'order__user__email', 'order__user__first_name'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'email_sent_at']
    date_hierarchy = 'issue_date'
    actions = ['generate_pdf_action', 'send_email_action']
    
    def total_amount_display(self, obj):
        return f"{obj.total_amount:.2f} EGP"
    total_amount_display.short_description = 'Total'
    total_amount_display.admin_order_field = 'total_amount'
    
    def generate_pdf_action(self, request, queryset):
        """Admin action to generate PDFs for selected invoices"""
        from .services import invoice_generator
        from django.core.files.base import ContentFile
        
        count = 0
        for invoice in queryset:
            try:
                pdf_buffer = invoice_generator.generate_invoice_pdf(invoice)
                invoice.pdf_file.save(
                    f'invoice_{invoice.invoice_number}.pdf',
                    ContentFile(pdf_buffer.getvalue()),
                    save=True
                )
                count += 1
            except Exception:
                pass
        
        self.message_user(
            request,
            f"Generated PDFs for {count} invoices."
        )
    generate_pdf_action.short_description = "Generate PDF for selected invoices"
    
    def send_email_action(self, request, queryset):
        """Admin action to send invoices via email"""
        # Implementation for sending emails
        count = queryset.filter(status='draft').update(
            status='sent',
            email_sent=True
        )
        self.message_user(
            request,
            f"Marked {count} invoices as sent."
        )
    send_email_action.short_description = "Mark selected invoices as sent"
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ShippingLabel)
class ShippingLabelAdmin(admin.ModelAdmin):
    list_display = [
        'label_number', 'order', 'recipient_name',
        'city', 'governorate', 'shipping_cost_display',
        'cash_on_delivery_display', 'created_at'
    ]
    list_filter = [
        'governorate', 'city', 'shipping_method', 'created_at'
    ]
    search_fields = [
        'label_number', 'order__order_number', 'recipient_name',
        'recipient_phone', 'tracking_number'
    ]
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    actions = ['generate_pdf_action']
    
    def shipping_cost_display(self, obj):
        return f"{obj.shipping_cost:.2f} EGP"
    shipping_cost_display.short_description = 'Shipping Cost'
    shipping_cost_display.admin_order_field = 'shipping_cost'
    
    def cash_on_delivery_display(self, obj):
        if obj.cash_on_delivery > 0:
            return f"{obj.cash_on_delivery:.2f} EGP"
        return "-"
    cash_on_delivery_display.short_description = 'COD Amount'
    cash_on_delivery_display.admin_order_field = 'cash_on_delivery'
    
    def generate_pdf_action(self, request, queryset):
        """Admin action to generate PDFs for selected shipping labels"""
        from .services import label_generator
        from django.core.files.base import ContentFile
        
        count = 0
        for label in queryset:
            try:
                pdf_buffer = label_generator.generate_shipping_label_pdf(label)
                label.pdf_file.save(
                    f'shipping_label_{label.label_number}.pdf',
                    ContentFile(pdf_buffer.getvalue()),
                    save=True
                )
                count += 1
            except Exception:
                pass
        
        self.message_user(
            request,
            f"Generated PDFs for {count} shipping labels."
        )
    generate_pdf_action.short_description = "Generate PDF for selected labels"
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = [
        'report_type', 'start_date', 'end_date',
        'total_revenue_display', 'net_profit_display',
        'profit_margin_display', 'generated_at', 'generated_by'
    ]
    list_filter = [
        'report_type', 'report_format', 'generated_at', 'generated_by'
    ]
    search_fields = ['report_type', 'start_date', 'end_date']
    readonly_fields = [
        'id', 'total_revenue', 'total_costs', 'total_expenses',
        'gross_profit', 'net_profit', 'profit_margin',
        'total_orders', 'average_order_value',
        'generated_at'
    ]
    date_hierarchy = 'generated_at'
    
    def total_revenue_display(self, obj):
        return f"{obj.total_revenue:,.2f} EGP"
    total_revenue_display.short_description = 'Revenue'
    total_revenue_display.admin_order_field = 'total_revenue'
    
    def net_profit_display(self, obj):
        color = 'green' if obj.net_profit > 0 else 'red'
        return format_html(
            '<span style="color: {};">{:,.2f} EGP</span>',
            color, obj.net_profit
        )
    net_profit_display.short_description = 'Net Profit'
    net_profit_display.admin_order_field = 'net_profit'
    
    def profit_margin_display(self, obj):
        color = 'green' if obj.profit_margin > 0 else 'red'
        return format_html(
            '<span style="color: {};">{:.2f}%</span>',
            color, obj.profit_margin
        )
    profit_margin_display.short_description = 'Margin %'
    profit_margin_display.admin_order_field = 'profit_margin'
    
    def save_model(self, request, obj, form, change):
        if not obj.generated_by:
            obj.generated_by = request.user
        super().save_model(request, obj, form, change)


# Customize admin site header
admin.site.site_header = "Soleva Accounting System"
admin.site.site_title = "Soleva Admin"
admin.site.index_title = "Accounting & Financial Management"
