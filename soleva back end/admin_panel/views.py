from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, Q, F
from django.db import models
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from users.models import User
from products.models import Product, Category
from orders.models import Order
from tracking.models import TrackingEvent


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_dashboard(request):
    """Admin dashboard overview"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Quick stats
    total_orders = Order.objects.count()
    total_customers = User.objects.filter(is_active=True, is_staff=False).count()
    total_products = Product.objects.filter(is_active=True).count()
    
    # Today's stats
    today_orders = Order.objects.filter(created_at__date=today).count()
    today_revenue = Order.objects.filter(
        created_at__date=today,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Recent activity
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    recent_customers = User.objects.filter(
        is_active=True, 
        is_staff=False
    ).order_by('-date_joined')[:5]
    
    # Pending actions
    pending_orders = Order.objects.filter(status='pending').count()
    low_stock_products = Product.objects.filter(
        track_inventory=True,
        inventory_quantity__lte=F('low_stock_threshold')
    ).count()
    
    dashboard_data = {
        'quick_stats': {
            'total_orders': total_orders,
            'total_customers': total_customers,
            'total_products': total_products,
            'today_orders': today_orders,
            'today_revenue': today_revenue,
        },
        'recent_activity': {
            'recent_orders': [
                {
                    'id': order.id,
                    'order_number': order.order_number,
                    'customer_name': order.customer_name,
                    'total_amount': order.total_amount,
                    'status': order.status,
                    'created_at': order.created_at,
                }
                for order in recent_orders
            ],
            'recent_customers': [
                {
                    'id': user.id,
                    'full_name': user.full_name,
                    'email': user.email,
                    'date_joined': user.date_joined,
                }
                for user in recent_customers
            ],
        },
        'pending_actions': {
            'pending_orders': pending_orders,
            'low_stock_products': low_stock_products,
        }
    }
    
    return Response(dashboard_data)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def overview_stats(request):
    """Overview statistics"""
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Orders stats
    total_orders = Order.objects.count()
    today_orders = Order.objects.filter(created_at__date=today).count()
    yesterday_orders = Order.objects.filter(created_at__date=yesterday).count()
    week_orders = Order.objects.filter(created_at__date__gte=week_ago).count()
    month_orders = Order.objects.filter(created_at__date__gte=month_ago).count()
    
    # Revenue stats
    total_revenue = Order.objects.filter(
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    today_revenue = Order.objects.filter(
        created_at__date=today,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    yesterday_revenue = Order.objects.filter(
        created_at__date=yesterday,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Customer stats
    total_customers = User.objects.filter(is_active=True, is_staff=False).count()
    new_customers_today = User.objects.filter(
        date_joined__date=today,
        is_staff=False
    ).count()
    
    # Product stats
    total_products = Product.objects.filter(is_active=True).count()
    out_of_stock = Product.objects.filter(
        is_active=True,
        track_inventory=True,
        inventory_quantity=0
    ).count()
    
    # Calculate growth rates
    order_growth = ((today_orders - yesterday_orders) / yesterday_orders * 100) if yesterday_orders > 0 else 0
    revenue_growth = ((today_revenue - yesterday_revenue) / yesterday_revenue * 100) if yesterday_revenue > 0 else 0
    
    stats = {
        'orders': {
            'total': total_orders,
            'today': today_orders,
            'week': week_orders,
            'month': month_orders,
            'growth_rate': order_growth,
        },
        'revenue': {
            'total': total_revenue,
            'today': today_revenue,
            'growth_rate': revenue_growth,
        },
        'customers': {
            'total': total_customers,
            'new_today': new_customers_today,
        },
        'products': {
            'total': total_products,
            'out_of_stock': out_of_stock,
        }
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def sales_stats(request):
    """Sales statistics"""
    days = int(request.GET.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)
    
    # Sales by day
    daily_sales = Order.objects.filter(
        created_at__date__gte=start_date,
        payment_status='paid'
    ).extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(
        orders=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('day')
    
    # Sales by status
    status_breakdown = Order.objects.filter(
        created_at__date__gte=start_date
    ).values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Top selling products
    from orders.models import OrderItem
    top_products = OrderItem.objects.filter(
        order__created_at__date__gte=start_date,
        order__payment_status='paid'
    ).values('product_name').annotate(
        quantity_sold=Sum('quantity'),
        revenue=Sum('total_price')
    ).order_by('-quantity_sold')[:10]
    
    # Average order value
    avg_order_value = Order.objects.filter(
        created_at__date__gte=start_date,
        payment_status='paid'
    ).aggregate(avg=Avg('total_amount'))['avg'] or Decimal('0.00')
    
    stats = {
        'daily_sales': list(daily_sales),
        'status_breakdown': list(status_breakdown),
        'top_products': list(top_products),
        'average_order_value': avg_order_value,
        'period_days': days,
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def customer_stats(request):
    """Customer statistics"""
    days = int(request.GET.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)
    
    # New customers by day
    daily_signups = User.objects.filter(
        date_joined__date__gte=start_date,
        is_staff=False
    ).extra(
        select={'day': 'date(date_joined)'}
    ).values('day').annotate(
        signups=Count('id')
    ).order_by('day')
    
    # Customer segments
    total_customers = User.objects.filter(is_active=True, is_staff=False).count()
    verified_customers = User.objects.filter(
        is_active=True, 
        is_staff=False, 
        is_verified=True
    ).count()
    
    # Top customers by orders
    top_customers = User.objects.filter(
        is_staff=False,
        orders__created_at__date__gte=start_date
    ).annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__total_amount')
    ).order_by('-total_spent')[:10]
    
    # Customer locations (top governorates)
    top_locations = Order.objects.filter(
        created_at__date__gte=start_date
    ).values('shipping_governorate').annotate(
        customer_count=Count('user', distinct=True)
    ).order_by('-customer_count')[:10]
    
    stats = {
        'daily_signups': list(daily_signups),
        'total_customers': total_customers,
        'verified_customers': verified_customers,
        'verification_rate': (verified_customers / total_customers * 100) if total_customers > 0 else 0,
        'top_customers': [
            {
                'id': customer.id,
                'full_name': customer.full_name,
                'email': customer.email,
                'order_count': customer.order_count,
                'total_spent': customer.total_spent,
            }
            for customer in top_customers
        ],
        'top_locations': list(top_locations),
        'period_days': days,
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def product_stats(request):
    """Product statistics"""
    # Inventory stats
    total_products = Product.objects.filter(is_active=True).count()
    in_stock = Product.objects.filter(
        Q(track_inventory=False) | Q(track_inventory=True, inventory_quantity__gt=0),
        is_active=True,
    ).count()
    
    out_of_stock = Product.objects.filter(
        is_active=True,
        track_inventory=True,
        inventory_quantity=0
    ).count()
    
    low_stock = Product.objects.filter(
        is_active=True,
        track_inventory=True,
        inventory_quantity__lte=F('low_stock_threshold'),
        inventory_quantity__gt=0
    ).count()
    
    # Category breakdown
    category_breakdown = Product.objects.filter(
        is_active=True
    ).values('category__name_en').annotate(
        product_count=Count('id')
    ).order_by('-product_count')
    
    # Featured products
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).count()
    
    stats = {
        'inventory': {
            'total_products': total_products,
            'in_stock': in_stock,
            'out_of_stock': out_of_stock,
            'low_stock': low_stock,
            'stock_rate': (in_stock / total_products * 100) if total_products > 0 else 0,
        },
        'category_breakdown': list(category_breakdown),
        'featured_products': featured_products,
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def low_stock_products(request):
    """Get low stock products"""
    low_stock = Product.objects.filter(
        is_active=True,
        track_inventory=True,
        inventory_quantity__lte=F('low_stock_threshold')
    ).select_related('category', 'brand').order_by('inventory_quantity')
    
    products = [
        {
            'id': product.id,
            'name': product.name_en,
            'sku': product.sku,
            'category': product.category.name_en if product.category else '',
            'inventory_quantity': product.inventory_quantity,
            'low_stock_threshold': product.low_stock_threshold,
            'price': product.price,
        }
        for product in low_stock
    ]
    
    return Response({
        'products': products,
        'count': len(products)
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def pending_orders(request):
    """Get pending orders"""
    orders = Order.objects.filter(
        status='pending'
    ).select_related('user').order_by('-created_at')
    
    order_data = [
        {
            'id': order.id,
            'order_number': order.order_number,
            'customer_name': order.customer_name,
            'customer_email': order.customer_email,
            'total_amount': order.total_amount,
            'payment_method': order.payment_method,
            'created_at': order.created_at,
        }
        for order in orders
    ]
    
    return Response({
        'orders': order_data,
        'count': len(order_data)
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def recent_customers(request):
    """Get recent customers"""
    limit = int(request.GET.get('limit', 10))
    
    customers = User.objects.filter(
        is_active=True,
        is_staff=False
    ).order_by('-date_joined')[:limit]
    
    customer_data = [
        {
            'id': customer.id,
            'full_name': customer.full_name,
            'email': customer.email,
            'phone_number': str(customer.phone_number) if customer.phone_number else '',
            'is_verified': customer.is_verified,
            'date_joined': customer.date_joined,
            'last_login': customer.last_login,
        }
        for customer in customers
    ]
    
    return Response({
        'customers': customer_data,
        'count': len(customer_data)
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def sales_report(request):
    """Sales report with detailed analytics"""
    days = int(request.GET.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)
    
    # Sales summary
    total_orders = Order.objects.filter(created_at__date__gte=start_date).count()
    paid_orders = Order.objects.filter(
        created_at__date__gte=start_date,
        payment_status='paid'
    ).count()
    total_revenue = Order.objects.filter(
        created_at__date__gte=start_date,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Payment method breakdown
    payment_methods = Order.objects.filter(
        created_at__date__gte=start_date,
        payment_status='paid'
    ).values('payment_method').annotate(
        count=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('-revenue')
    
    # Daily sales trend
    daily_sales = Order.objects.filter(
        created_at__date__gte=start_date,
        payment_status='paid'
    ).extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(
        orders=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('day')
    
    report_data = {
        'summary': {
            'total_orders': total_orders,
            'paid_orders': paid_orders,
            'total_revenue': total_revenue,
            'conversion_rate': (paid_orders / total_orders * 100) if total_orders > 0 else 0,
        },
        'payment_methods': list(payment_methods),
        'daily_sales': list(daily_sales),
        'period_days': days,
    }
    
    return Response(report_data)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def customer_report(request):
    """Customer report with detailed analytics"""
    days = int(request.GET.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)
    
    # Customer summary
    total_customers = User.objects.filter(is_active=True, is_staff=False).count()
    new_customers = User.objects.filter(
        date_joined__date__gte=start_date,
        is_staff=False
    ).count()
    
    # Customer activity
    active_customers = User.objects.filter(
        is_staff=False,
        orders__created_at__date__gte=start_date
    ).distinct().count()
    
    # Customer segments
    verified_customers = User.objects.filter(
        is_active=True,
        is_staff=False,
        is_verified=True
    ).count()
    
    # Top customers by spending
    top_customers = User.objects.filter(
        is_staff=False,
        orders__created_at__date__gte=start_date,
        orders__payment_status='paid'
    ).annotate(
        total_spent=Sum('orders__total_amount'),
        order_count=Count('orders')
    ).order_by('-total_spent')[:10]
    
    report_data = {
        'summary': {
            'total_customers': total_customers,
            'new_customers': new_customers,
            'active_customers': active_customers,
            'verified_customers': verified_customers,
            'verification_rate': (verified_customers / total_customers * 100) if total_customers > 0 else 0,
        },
        'top_customers': [
            {
                'id': customer.id,
                'full_name': customer.full_name,
                'email': customer.email,
                'total_spent': customer.total_spent,
                'order_count': customer.order_count,
            }
            for customer in top_customers
        ],
        'period_days': days,
    }
    
    return Response(report_data)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def inventory_report(request):
    """Inventory report with stock analysis"""
    # Stock levels
    total_products = Product.objects.filter(is_active=True).count()
    in_stock = Product.objects.filter(
        Q(track_inventory=False) | Q(track_inventory=True, inventory_quantity__gt=0),
        is_active=True,
    ).count()
    
    out_of_stock = Product.objects.filter(
        is_active=True,
        track_inventory=True,
        inventory_quantity=0
    ).count()
    
    low_stock = Product.objects.filter(
        is_active=True,
        track_inventory=True,
        inventory_quantity__lte=F('low_stock_threshold'),
        inventory_quantity__gt=0
    ).count()
    
    # Category breakdown
    category_stock = Product.objects.filter(
        is_active=True
    ).values('category__name_en').annotate(
        total_products=Count('id'),
        in_stock=Count('id', filter=Q(
            Q(track_inventory=False) | Q(track_inventory=True, inventory_quantity__gt=0)
        )),
        out_of_stock=Count('id', filter=Q(
            track_inventory=True, inventory_quantity=0
        )),
        low_stock=Count('id', filter=Q(
            track_inventory=True,
            inventory_quantity__lte=F('low_stock_threshold'),
            inventory_quantity__gt=0
        ))
    ).order_by('-total_products')
    
    # Low stock products details
    low_stock_products = Product.objects.filter(
        is_active=True,
        track_inventory=True,
        inventory_quantity__lte=F('low_stock_threshold')
    ).select_related('category').order_by('inventory_quantity')
    
    report_data = {
        'summary': {
            'total_products': total_products,
            'in_stock': in_stock,
            'out_of_stock': out_of_stock,
            'low_stock': low_stock,
            'stock_rate': (in_stock / total_products * 100) if total_products > 0 else 0,
        },
        'category_breakdown': list(category_stock),
        'low_stock_products': [
            {
                'id': product.id,
                'name': product.name_en,
                'sku': product.sku,
                'category': product.category.name_en if product.category else '',
                'inventory_quantity': product.inventory_quantity,
                'low_stock_threshold': product.low_stock_threshold,
                'price': product.price,
            }
            for product in low_stock_products
        ],
    }
    
    return Response(report_data)
