"""
Accounting services for PDF generation, calculations, and reports
"""

import os
from io import BytesIO
from decimal import Decimal
from datetime import datetime, timedelta
from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
from .models import (
    SalesRecord, BusinessExpense, InventoryTransaction,
    Invoice, ShippingLabel, FinancialReport, ProductCost
)
from orders.models import Order


class PDFInvoiceGenerator:
    """Generate professional PDF invoices with Arabic support"""
    
    def __init__(self):
        self.setup_fonts()
        self.page_width, self.page_height = A4
        self.margin = 2 * cm
    
    def setup_fonts(self):
        """Setup Arabic and English fonts"""
        try:
            # Try to register Arabic font (you'll need to add Arabic font files)
            # pdfmetrics.registerFont(TTFont('Arabic', 'path/to/arabic-font.ttf'))
            pass
        except:
            pass  # Fallback to default fonts
    
    def generate_invoice_pdf(self, invoice):
        """Generate PDF for invoice"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        # Build story
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            textColor=colors.HexColor('#d1b16a'),
            alignment=TA_CENTER
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#333333'),
        )
        
        # Company Header
        story.append(Paragraph("SOLEVA", title_style))
        story.append(Paragraph("فاتورة مبيعات | Sales Invoice", header_style))
        story.append(Spacer(1, 20))
        
        # Invoice details table
        invoice_data = [
            ['Invoice Number | رقم الفاتورة:', invoice.invoice_number],
            ['Date | التاريخ:', invoice.issue_date.strftime('%Y-%m-%d')],
            ['Order Number | رقم الطلب:', invoice.order.order_number],
            ['Customer | العميل:', f"{invoice.order.user.first_name} {invoice.order.user.last_name}"],
        ]
        
        invoice_table = Table(invoice_data, colWidths=[4*cm, 8*cm])
        invoice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ]))
        
        story.append(invoice_table)
        story.append(Spacer(1, 30))
        
        # Items table
        items_data = [['Product | المنتج', 'Qty | الكمية', 'Unit Price | السعر', 'Total | الإجمالي']]
        
        for item in invoice.order.items.all():
            items_data.append([
                item.product.name,
                str(item.quantity),
                f"{item.unit_price} EGP",
                f"{item.total_price} EGP"
            ])
        
        # Add totals rows
        items_data.extend([
            ['', '', 'Subtotal | المجموع الفرعي:', f"{invoice.subtotal} EGP"],
            ['', '', 'Shipping | الشحن:', f"{invoice.shipping_amount} EGP"],
            ['', '', 'Discount | الخصم:', f"-{invoice.discount_amount} EGP"],
            ['', '', 'Total | الإجمالي:', f"{invoice.total_amount} EGP"],
        ])
        
        items_table = Table(items_data, colWidths=[6*cm, 2*cm, 3*cm, 3*cm])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d1b16a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            # Highlight total rows
            ('BACKGROUND', (0, -4), (-1, -1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 30))
        
        # Footer
        footer_text = """
        <para align="center">
        شكراً لتسوقك معنا | Thank you for shopping with us<br/>
        <b>SOLEVA</b> - Premium Products<br/>
        Website: thesoleva.com | Email: info@thesoleva.com
        </para>
        """
        story.append(Paragraph(footer_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer


class PDFShippingLabelGenerator:
    """Generate shipping labels / بوليصات شحن"""
    
    def generate_shipping_label_pdf(self, shipping_label):
        """Generate PDF shipping label"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'ShippingTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#d1b16a'),
            alignment=TA_CENTER
        )
        
        story.append(Paragraph("بوليصة شحن | Shipping Label", title_style))
        story.append(Spacer(1, 20))
        
        # Shipping details
        shipping_data = [
            ['Label Number | رقم البوليصة:', shipping_label.label_number],
            ['Order Number | رقم الطلب:', shipping_label.order.order_number],
            ['Recipient | المستلم:', shipping_label.recipient_name],
            ['Phone | الهاتف:', shipping_label.recipient_phone],
            ['Address | العنوان:', shipping_label.delivery_address],
            ['City | المدينة:', f"{shipping_label.city}, {shipping_label.governorate}"],
            ['Shipping Cost | تكلفة الشحن:', f"{shipping_label.shipping_cost} EGP"],
            ['COD Amount | الدفع عند الاستلام:', f"{shipping_label.cash_on_delivery} EGP"],
        ]
        
        shipping_table = Table(shipping_data, colWidths=[5*cm, 8*cm])
        shipping_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(shipping_table)
        story.append(Spacer(1, 30))
        
        # Barcode placeholder (you can integrate with barcode libraries)
        story.append(Paragraph("Tracking: " + (shipping_label.tracking_number or "To be assigned"), styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        
        return buffer


class FinancialCalculationService:
    """Service for financial calculations and analytics"""
    
    @staticmethod
    def calculate_period_profit(start_date, end_date):
        """Calculate profit for a specific period"""
        sales = SalesRecord.objects.filter(
            sale_date__date__range=[start_date, end_date],
            is_return=False
        )
        
        total_revenue = sales.aggregate(Sum('gross_revenue'))['gross_revenue__sum'] or Decimal('0.00')
        total_cogs = sales.aggregate(Sum('total_cost_of_goods'))['total_cost_of_goods__sum'] or Decimal('0.00')
        gross_profit = total_revenue - total_cogs
        
        # Calculate expenses for the period
        expenses = BusinessExpense.objects.filter(
            expense_date__range=[start_date, end_date]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        net_profit = gross_profit - expenses
        
        return {
            'total_revenue': total_revenue,
            'total_cogs': total_cogs,
            'gross_profit': gross_profit,
            'total_expenses': expenses,
            'net_profit': net_profit,
            'profit_margin': (net_profit / total_revenue * 100) if total_revenue > 0 else Decimal('0.00')
        }
    
    @staticmethod
    def get_top_selling_products(start_date, end_date, limit=10):
        """Get top selling products for period"""
        from django.db.models import Sum
        from orders.models import OrderItem
        
        top_products = OrderItem.objects.filter(
            order__created_at__date__range=[start_date, end_date],
            order__status='completed'
        ).values(
            'product__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('total_price')
        ).order_by('-total_quantity')[:limit]
        
        return top_products
    
    @staticmethod
    def get_inventory_valuation():
        """Calculate total inventory value based on current stock and costs"""
        products_with_cost = ProductCost.objects.select_related('product').all()
        
        total_value = Decimal('0.00')
        inventory_data = []
        
        for product_cost in products_with_cost:
            product = product_cost.product
            stock_value = product.stock_quantity * product_cost.total_cost
            total_value += stock_value
            
            inventory_data.append({
                'product_name': product.name,
                'stock_quantity': product.stock_quantity,
                'unit_cost': product_cost.total_cost,
                'total_value': stock_value
            })
        
        return {
            'total_inventory_value': total_value,
            'items': inventory_data
        }


class ReportGenerationService:
    """Service for generating financial reports"""
    
    def __init__(self):
        self.pdf_generator = PDFInvoiceGenerator()
        self.calc_service = FinancialCalculationService()
    
    def generate_period_report(self, start_date, end_date, report_type='custom'):
        """Generate comprehensive financial report for period"""
        
        # Calculate financial metrics
        financial_data = self.calc_service.calculate_period_profit(start_date, end_date)
        
        # Get order statistics
        orders = Order.objects.filter(
            created_at__date__range=[start_date, end_date],
            status='completed'
        )
        
        total_orders = orders.count()
        avg_order_value = orders.aggregate(Avg('total_amount'))['total_amount__avg'] or Decimal('0.00')
        
        # Create report record
        report = FinancialReport.objects.create(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            total_revenue=financial_data['total_revenue'],
            total_costs=financial_data['total_cogs'],
            total_expenses=financial_data['total_expenses'],
            gross_profit=financial_data['gross_profit'],
            net_profit=financial_data['net_profit'],
            profit_margin=financial_data['profit_margin'],
            total_orders=total_orders,
            average_order_value=avg_order_value
        )
        
        # Generate PDF report
        pdf_buffer = self._generate_report_pdf(report, financial_data)
        report.pdf_file.save(
            f'financial_report_{start_date}_{end_date}.pdf',
            ContentFile(pdf_buffer.getvalue()),
            save=True
        )
        
        # Generate Excel report
        excel_buffer = self._generate_report_excel(report, financial_data)
        report.excel_file.save(
            f'financial_report_{start_date}_{end_date}.xlsx',
            ContentFile(excel_buffer.getvalue()),
            save=True
        )
        
        return report
    
    def _generate_report_pdf(self, report, financial_data):
        """Generate PDF report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title = f"Financial Report | تقرير مالي"
        story.append(Paragraph(title, styles['Title']))
        story.append(Spacer(1, 20))
        
        # Period
        period = f"Period: {report.start_date} to {report.end_date}"
        story.append(Paragraph(period, styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # Financial summary table
        summary_data = [
            ['Metric | المؤشر', 'Amount (EGP) | المبلغ'],
            ['Total Revenue | إجمالي الإيرادات', f"{report.total_revenue:,.2f}"],
            ['Cost of Goods Sold | تكلفة البضاعة المباعة', f"{report.total_costs:,.2f}"],
            ['Gross Profit | الربح الإجمالي', f"{report.gross_profit:,.2f}"],
            ['Total Expenses | إجمالي المصروفات', f"{report.total_expenses:,.2f}"],
            ['Net Profit | صافي الربح', f"{report.net_profit:,.2f}"],
            ['Profit Margin | هامش الربح', f"{report.profit_margin:.2f}%"],
            ['Total Orders | إجمالي الطلبات', f"{report.total_orders}"],
            ['Average Order Value | متوسط قيمة الطلب', f"{report.average_order_value:,.2f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[8*cm, 4*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d1b16a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(summary_table)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _generate_report_excel(self, report, financial_data):
        """Generate Excel report with charts"""
        import io
        import xlsxwriter
        
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        
        # Summary worksheet
        summary_sheet = workbook.add_worksheet('Financial Summary')
        
        # Formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#d1b16a',
            'font_color': 'white',
            'border': 1
        })
        
        currency_format = workbook.add_format({
            'num_format': '#,##0.00',
            'border': 1
        })
        
        # Headers
        summary_sheet.write('A1', 'Financial Summary', header_format)
        summary_sheet.write('A3', 'Metric', header_format)
        summary_sheet.write('B3', 'Amount (EGP)', header_format)
        
        # Data
        metrics = [
            ('Total Revenue', report.total_revenue),
            ('Cost of Goods Sold', report.total_costs),
            ('Gross Profit', report.gross_profit),
            ('Total Expenses', report.total_expenses),
            ('Net Profit', report.net_profit),
            ('Total Orders', report.total_orders),
            ('Average Order Value', report.average_order_value),
        ]
        
        for i, (metric, value) in enumerate(metrics, 4):
            summary_sheet.write(f'A{i}', metric)
            summary_sheet.write(f'B{i}', float(value), currency_format)
        
        # Auto-adjust column width
        summary_sheet.set_column('A:A', 25)
        summary_sheet.set_column('B:B', 15)
        
        workbook.close()
        buffer.seek(0)
        return buffer


# Service instances
invoice_generator = PDFInvoiceGenerator()
label_generator = PDFShippingLabelGenerator()
report_service = ReportGenerationService()
calculation_service = FinancialCalculationService()
