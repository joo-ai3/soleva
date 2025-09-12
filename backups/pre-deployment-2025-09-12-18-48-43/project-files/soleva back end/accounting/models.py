"""
Soleva Accounting System Models
All monetary values are stored in Egyptian Pounds (EGP) as Decimal fields
"""

from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from orders.models import Order, OrderItem
from products.models import Product, ProductVariant
import uuid

User = get_user_model()

class Currency(models.Model):
    """Currency model - locked to EGP only for Soleva"""
    code = models.CharField(_('Currency Code'), max_length=3, default='EGP')
    name = models.CharField(_('Currency Name'), max_length=50, default='Egyptian Pound')
    symbol = models.CharField(_('Currency Symbol'), max_length=5, default='ج.م')
    is_active = models.BooleanField(_('Is Active'), default=True)
    
    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class ProductCost(models.Model):
    """Track real production costs for each product"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='cost_info')
    production_cost = models.DecimalField(
        _('Production Cost (EGP)'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_('Actual production cost per unit in EGP')
    )
    packaging_cost = models.DecimalField(
        _('Packaging Cost (EGP)'),
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    last_updated = models.DateTimeField(_('Last Updated'), auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(_('Cost Notes'), blank=True)
    
    class Meta:
        verbose_name = _('Product Cost')
        verbose_name_plural = _('Product Costs')
    
    def __str__(self):
        return f"{self.product.name} - {self.total_cost} EGP"
    
    @property
    def total_cost(self):
        """Total cost per unit including production and packaging"""
        return self.production_cost + self.packaging_cost

class InventoryTransaction(models.Model):
    """Track all inventory movements"""
    TRANSACTION_TYPES = [
        ('stock_in', _('Stock In')),
        ('stock_out', _('Stock Out')),
        ('sale', _('Sale')),
        ('return', _('Return')),
        ('adjustment', _('Adjustment')),
        ('damaged', _('Damaged')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_transactions')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True, related_name='inventory_transactions')
    transaction_type = models.CharField(_('Transaction Type'), max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField(_('Quantity'))
    previous_stock = models.IntegerField(_('Previous Stock'))
    new_stock = models.IntegerField(_('New Stock'))
    unit_cost = models.DecimalField(
        _('Unit Cost (EGP)'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        blank=True
    )
    total_cost = models.DecimalField(
        _('Total Cost (EGP)'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        blank=True
    )
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_transactions')
    reference_number = models.CharField(_('Reference Number'), max_length=100, blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = _('Inventory Transaction')
        verbose_name_plural = _('Inventory Transactions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_type} - {self.product.name} ({self.quantity}) - {self.created_at.date()}"

class ExpenseCategory(models.Model):
    """Categories for business expenses"""
    name_en = models.CharField(_('Name (English)'), max_length=100)
    name_ar = models.CharField(_('Name (Arabic)'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Expense Category')
        verbose_name_plural = _('Expense Categories')
    
    def __str__(self):
        return self.name_en

class BusinessExpense(models.Model):
    """Track all business expenses in EGP"""
    EXPENSE_TYPES = [
        ('advertising', _('Advertising')),
        ('design', _('Design')),
        ('photography', _('Photography')),
        ('shipping', _('Shipping')),
        ('packaging', _('Packaging Materials')),
        ('office', _('Office Expenses')),
        ('utilities', _('Utilities')),
        ('software', _('Software/Tools')),
        ('marketing', _('Marketing')),
        ('other', _('Other')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, related_name='expenses')
    expense_type = models.CharField(_('Expense Type'), max_length=20, choices=EXPENSE_TYPES)
    title = models.CharField(_('Expense Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    amount = models.DecimalField(
        _('Amount (EGP)'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    expense_date = models.DateField(_('Expense Date'))
    payment_method = models.CharField(_('Payment Method'), max_length=50, blank=True)
    receipt_number = models.CharField(_('Receipt/Invoice Number'), max_length=100, blank=True)
    supplier_vendor = models.CharField(_('Supplier/Vendor'), max_length=200, blank=True)
    is_recurring = models.BooleanField(_('Is Recurring'), default=False)
    recurring_frequency = models.CharField(
        _('Recurring Frequency'),
        max_length=20,
        choices=[
            ('daily', _('Daily')),
            ('weekly', _('Weekly')),
            ('monthly', _('Monthly')),
            ('quarterly', _('Quarterly')),
            ('yearly', _('Yearly')),
        ],
        blank=True
    )
    tags = models.CharField(_('Tags'), max_length=200, blank=True, help_text=_('Comma-separated tags'))
    receipt_file = models.FileField(_('Receipt File'), upload_to='receipts/%Y/%m/', blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = _('Business Expense')
        verbose_name_plural = _('Business Expenses')
        ordering = ['-expense_date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.amount} EGP - {self.expense_date}"

class SalesRecord(models.Model):
    """Comprehensive sales tracking linked to real orders"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='sales_record')
    gross_revenue = models.DecimalField(
        _('Gross Revenue (EGP)'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_cost_of_goods = models.DecimalField(
        _('Total Cost of Goods Sold (EGP)'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    shipping_cost = models.DecimalField(
        _('Shipping Cost (EGP)'),
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    packaging_cost = models.DecimalField(
        _('Packaging Cost (EGP)'),
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    payment_gateway_fee = models.DecimalField(
        _('Payment Gateway Fee (EGP)'),
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    discount_amount = models.DecimalField(
        _('Discount Amount (EGP)'),
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    coupon_discount = models.DecimalField(
        _('Coupon Discount (EGP)'),
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    gross_profit = models.DecimalField(
        _('Gross Profit (EGP)'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    net_profit = models.DecimalField(
        _('Net Profit (EGP)'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    profit_margin_percentage = models.DecimalField(
        _('Profit Margin %'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    sale_date = models.DateTimeField(_('Sale Date'))
    is_return = models.BooleanField(_('Is Return'), default=False)
    return_reason = models.TextField(_('Return Reason'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Sales Record')
        verbose_name_plural = _('Sales Records')
        ordering = ['-sale_date']
    
    def save(self, *args, **kwargs):
        """Auto-calculate profits on save"""
        self.calculate_profits()
        super().save(*args, **kwargs)
    
    def calculate_profits(self):
        """Calculate gross and net profit based on real data"""
        # Gross Profit = Revenue - Cost of Goods Sold
        self.gross_profit = self.gross_revenue - self.total_cost_of_goods
        
        # Net Profit = Gross Profit - All Other Costs
        total_expenses = (
            self.shipping_cost + 
            self.packaging_cost + 
            self.payment_gateway_fee + 
            self.discount_amount + 
            self.coupon_discount
        )
        self.net_profit = self.gross_profit - total_expenses
        
        # Profit Margin = (Net Profit / Revenue) * 100
        if self.gross_revenue > 0:
            self.profit_margin_percentage = (self.net_profit / self.gross_revenue) * 100
        else:
            self.profit_margin_percentage = Decimal('0.00')
    
    def __str__(self):
        return f"Sale #{self.order.order_number} - {self.net_profit} EGP profit"

class Invoice(models.Model):
    """Generated invoices for orders"""
    INVOICE_TYPES = [
        ('sale', _('Sales Invoice')),
        ('return', _('Return Invoice')),
        ('proforma', _('Proforma Invoice')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('sent', _('Sent')),
        ('paid', _('Paid')),
        ('overdue', _('Overdue')),
        ('cancelled', _('Cancelled')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(_('Invoice Number'), max_length=50, unique=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='invoices')
    invoice_type = models.CharField(_('Invoice Type'), max_length=20, choices=INVOICE_TYPES, default='sale')
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    issue_date = models.DateField(_('Issue Date'))
    due_date = models.DateField(_('Due Date'))
    subtotal = models.DecimalField(
        _('Subtotal (EGP)'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    tax_amount = models.DecimalField(
        _('Tax Amount (EGP)'),
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    shipping_amount = models.DecimalField(
        _('Shipping Amount (EGP)'),
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    discount_amount = models.DecimalField(
        _('Discount Amount (EGP)'),
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_amount = models.DecimalField(
        _('Total Amount (EGP)'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    notes = models.TextField(_('Notes'), blank=True)
    terms_conditions = models.TextField(_('Terms & Conditions'), blank=True)
    pdf_file = models.FileField(_('PDF File'), upload_to='invoices/%Y/%m/', blank=True)
    email_sent = models.BooleanField(_('Email Sent'), default=False)
    email_sent_at = models.DateTimeField(_('Email Sent At'), null=True, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.total_amount} EGP"
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        from datetime import datetime
        year = datetime.now().year
        month = datetime.now().month
        
        # Count invoices for current month
        count = Invoice.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).count() + 1
        
        return f"INV-{year}{month:02d}-{count:04d}"

class ShippingLabel(models.Model):
    """Generated shipping labels/بوليصات شحن"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping_label')
    label_number = models.CharField(_('Label Number'), max_length=50, unique=True)
    recipient_name = models.CharField(_('Recipient Name'), max_length=200)
    recipient_phone = models.CharField(_('Recipient Phone'), max_length=20)
    delivery_address = models.TextField(_('Delivery Address'))
    governorate = models.CharField(_('Governorate'), max_length=100)
    city = models.CharField(_('City'), max_length=100)
    postal_code = models.CharField(_('Postal Code'), max_length=20, blank=True)
    shipping_cost = models.DecimalField(
        _('Shipping Cost (EGP)'),
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    cash_on_delivery = models.DecimalField(
        _('Cash on Delivery (EGP)'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    shipping_method = models.CharField(_('Shipping Method'), max_length=100)
    tracking_number = models.CharField(_('Tracking Number'), max_length=100, blank=True)
    special_instructions = models.TextField(_('Special Instructions'), blank=True)
    pdf_file = models.FileField(_('PDF File'), upload_to='shipping_labels/%Y/%m/', blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = _('Shipping Label')
        verbose_name_plural = _('Shipping Labels')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Label {self.label_number} - {self.recipient_name}"
    
    def generate_label_number(self):
        """Generate unique label number"""
        from datetime import datetime
        year = datetime.now().year
        month = datetime.now().month
        day = datetime.now().day
        
        count = ShippingLabel.objects.filter(
            created_at__year=year,
            created_at__month=month,
            created_at__day=day
        ).count() + 1
        
        return f"SL-{year}{month:02d}{day:02d}-{count:04d}"

class FinancialReport(models.Model):
    """Generated financial reports"""
    REPORT_TYPES = [
        ('daily', _('Daily Report')),
        ('weekly', _('Weekly Report')),
        ('monthly', _('Monthly Report')),
        ('quarterly', _('Quarterly Report')),
        ('yearly', _('Yearly Report')),
        ('custom', _('Custom Period Report')),
    ]
    
    REPORT_FORMATS = [
        ('pdf', _('PDF')),
        ('excel', _('Excel')),
        ('both', _('PDF & Excel')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(_('Report Type'), max_length=20, choices=REPORT_TYPES)
    report_format = models.CharField(_('Report Format'), max_length=10, choices=REPORT_FORMATS, default='pdf')
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    total_revenue = models.DecimalField(
        _('Total Revenue (EGP)'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_costs = models.DecimalField(
        _('Total Costs (EGP)'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_expenses = models.DecimalField(
        _('Total Expenses (EGP)'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    gross_profit = models.DecimalField(
        _('Gross Profit (EGP)'),
        max_digits=15,
        decimal_places=2
    )
    net_profit = models.DecimalField(
        _('Net Profit (EGP)'),
        max_digits=15,
        decimal_places=2
    )
    profit_margin = models.DecimalField(
        _('Profit Margin %'),
        max_digits=5,
        decimal_places=2
    )
    total_orders = models.IntegerField(_('Total Orders'))
    average_order_value = models.DecimalField(
        _('Average Order Value (EGP)'),
        max_digits=10,
        decimal_places=2
    )
    pdf_file = models.FileField(_('PDF Report'), upload_to='reports/%Y/%m/', blank=True)
    excel_file = models.FileField(_('Excel Report'), upload_to='reports/%Y/%m/', blank=True)
    generated_at = models.DateTimeField(_('Generated At'), auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = _('Financial Report')
        verbose_name_plural = _('Financial Reports')
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.start_date} to {self.end_date}"
