from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from orders.models import Order, OrderStatusHistory


class Command(BaseCommand):
    help = 'Automatically update order statuses based on business rules'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if outside normal business hours',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        now = timezone.now()
        updated_orders = 0
        
        # Business rules for automatic status updates
        rules = [
            {
                'name': 'Auto-confirm paid orders',
                'filter': {
                    'status': 'pending',
                    'payment_status': 'payment_approved',
                    'created_at__gte': now - timedelta(hours=24)  # Only recent orders
                },
                'new_status': 'confirmed',
                'update_field': 'confirmed_at'
            },
            {
                'name': 'Auto-process confirmed orders after 2 hours',
                'filter': {
                    'status': 'confirmed',
                    'confirmed_at__lte': now - timedelta(hours=2),
                    'confirmed_at__gte': now - timedelta(days=7)  # Not too old
                },
                'new_status': 'processing',
                'update_field': None
            },
            {
                'name': 'Auto-ship processed orders after 1 day',
                'filter': {
                    'status': 'processing',
                    'updated_at__lte': now - timedelta(days=1),
                    'updated_at__gte': now - timedelta(days=5)  # Not too old
                },
                'new_status': 'shipped',
                'update_field': 'shipped_at'
            },
            {
                'name': 'Auto-deliver shipped orders after 3 days',
                'filter': {
                    'status': 'shipped',
                    'shipped_at__lte': now - timedelta(days=3),
                    'shipped_at__gte': now - timedelta(days=14)  # Not too old
                },
                'new_status': 'delivered',
                'update_field': 'delivered_at'
            }
        ]
        
        for rule in rules:
            self.stdout.write(f"\nProcessing rule: {rule['name']}")
            
            # Get orders matching the rule
            orders = Order.objects.filter(**rule['filter'])
            count = orders.count()
            
            if count == 0:
                self.stdout.write(f"  No orders found matching criteria")
                continue
                
            self.stdout.write(f"  Found {count} orders to update")
            
            if not dry_run:
                with transaction.atomic():
                    for order in orders:
                        old_status = order.status
                        order.status = rule['new_status']
                        
                        # Update timestamp field if specified
                        if rule['update_field']:
                            setattr(order, rule['update_field'], now)
                        
                        order.save()
                        
                        # Create status history
                        OrderStatusHistory.objects.create(
                            order=order,
                            previous_status=old_status,
                            new_status=rule['new_status'],
                            comment=f'Automatically updated by system: {rule["name"]}',
                            changed_by=None  # System update
                        )
                        
                        updated_orders += 1
                        
                        self.stdout.write(
                            f"  Updated order {order.order_number}: {old_status} → {rule['new_status']}"
                        )
            else:
                for order in orders:
                    self.stdout.write(
                        f"  Would update order {order.order_number}: {order.status} → {rule['new_status']}"
                    )
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\nDRY RUN: Would have updated {sum(Order.objects.filter(**rule["filter"]).count() for rule in rules)} orders')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully updated {updated_orders} orders')
            )
            
        # Additional checks and notifications
        self._check_stuck_orders()
        self._check_overdue_orders()
    
    def _check_stuck_orders(self):
        """Check for orders that haven't moved status in a long time"""
        now = timezone.now()
        
        stuck_orders = Order.objects.filter(
            status__in=['pending', 'confirmed', 'processing'],
            updated_at__lte=now - timedelta(days=7)
        ).count()
        
        if stuck_orders > 0:
            self.stdout.write(
                self.style.WARNING(f'WARNING: {stuck_orders} orders appear to be stuck (no status change in 7+ days)')
            )
    
    def _check_overdue_orders(self):
        """Check for orders that are overdue for delivery"""
        now = timezone.now()
        
        overdue_orders = Order.objects.filter(
            status__in=['shipped', 'out_for_delivery'],
            estimated_delivery_date__lte=now - timedelta(days=1),
            estimated_delivery_date__isnull=False
        ).count()
        
        if overdue_orders > 0:
            self.stdout.write(
                self.style.WARNING(f'WARNING: {overdue_orders} orders are overdue for delivery')
            )
