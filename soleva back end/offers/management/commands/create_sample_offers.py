from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from offers.models import FlashSale, SpecialOffer, FlashSaleProduct


class Command(BaseCommand):
    help = 'Create sample flash sales and special offers for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing offers before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing offers...')
            FlashSale.objects.all().delete()
            SpecialOffer.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing offers cleared.'))

        # Create Flash Sales
        self.stdout.write('Creating Flash Sales...')
        
        now = timezone.now()
        
        # Active Flash Sale (24 hours)
        flash_sale_1 = FlashSale.objects.create(
            name_en='Weekend Flash Sale',
            name_ar='عرض نهاية الأسبوع البرقي',
            description_en='Incredible discounts for the weekend only!',
            description_ar='خصومات لا تصدق لنهاية الأسبوع فقط!',
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=23),
            banner_color='#ff4444',
            text_color='#ffffff',
            display_priority=10,
            is_active=True,
            show_countdown=True,
            total_usage_limit=100
        )
        
        # Upcoming Flash Sale (starts in 2 hours)
        flash_sale_2 = FlashSale.objects.create(
            name_en='Midnight Flash Sale',
            name_ar='عرض منتصف الليل البرقي',
            description_en='Special midnight deals - limited time only!',
            description_ar='عروض منتصف الليل الخاصة - وقت محدود فقط!',
            start_time=now + timedelta(hours=2),
            end_time=now + timedelta(hours=8),
            banner_color='#8b5cf6',
            text_color='#ffffff',
            display_priority=5,
            is_active=True,
            show_countdown=True,
            total_usage_limit=50
        )

        # Create Special Offers
        self.stdout.write('Creating Special Offers...')
        
        # Buy 2 Get 1 Free
        special_offer_1 = SpecialOffer.objects.create(
            name_en='Buy 2 Get 1 Free',
            name_ar='اشتري 2 واحصل على 1 مجاناً',
            description_en='Purchase any 2 items and get the 3rd one absolutely free!',
            description_ar='اشتر أي منتجين واحصل على الثالث مجاناً تماماً!',
            offer_type='buy_x_get_y_free',
            buy_quantity=2,
            free_quantity=1,
            start_time=now - timedelta(days=1),
            end_time=now + timedelta(days=7),
            button_text_en='Activate Buy 2 Get 1 Free',
            button_text_ar='تفعيل اشتري 2 واحصل على 1 مجاناً',
            button_color='#10b981',
            highlight_color='#d1fae5',
            is_active=True,
            show_on_product_page=True,
            show_timer=True,
            total_usage_limit=200
        )
        
        # Buy 3 Get Free Shipping
        special_offer_2 = SpecialOffer.objects.create(
            name_en='Buy 3 Get Free Shipping',
            name_ar='اشتري 3 واحصل على شحن مجاني',
            description_en='Purchase 3 or more items and enjoy free shipping!',
            description_ar='اشتر 3 منتجات أو أكثر واستمتع بالشحن المجاني!',
            offer_type='buy_x_free_shipping',
            buy_quantity=3,
            start_time=now - timedelta(hours=12),
            end_time=now + timedelta(days=3),
            button_text_en='Get Free Shipping',
            button_text_ar='احصل على شحن مجاني',
            button_color='#3b82f6',
            highlight_color='#dbeafe',
            is_active=True,
            show_on_product_page=True,
            show_timer=True,
            total_usage_limit=150
        )
        
        # Bundle Discount - 20% off
        special_offer_3 = SpecialOffer.objects.create(
            name_en='Bundle Deal - 20% Off',
            name_ar='عرض الحزمة - خصم 20%',
            description_en='Mix and match any 2 different items for 20% off!',
            description_ar='امزج واختر أي منتجين مختلفين واحصل على خصم 20%!',
            offer_type='bundle_discount',
            buy_quantity=2,
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            start_time=now - timedelta(hours=6),
            end_time=now + timedelta(days=5),
            button_text_en='Activate Bundle Deal',
            button_text_ar='تفعيل عرض الحزمة',
            button_color='#f59e0b',
            highlight_color='#fef3c7',
            is_active=True,
            show_on_product_page=True,
            show_timer=True,
            total_usage_limit=100
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'- {FlashSale.objects.count()} Flash Sales\n'
                f'- {SpecialOffer.objects.count()} Special Offers\n\n'
                f'Flash Sales:\n'
                f'- {flash_sale_1.name_en} (Active - ends in ~23 hours)\n'
                f'- {flash_sale_2.name_en} (Upcoming - starts in 2 hours)\n\n'
                f'Special Offers:\n'
                f'- {special_offer_1.name_en} (Active for 7 days)\n'
                f'- {special_offer_2.name_en} (Active for 3 days)\n'
                f'- {special_offer_3.name_en} (Active for 5 days)'
            )
        )
        
        self.stdout.write(
            self.style.WARNING(
                '\nNote: To test Flash Sale products, you need to add FlashSaleProduct entries '
                'linking specific products to the flash sales via the admin interface.'
            )
        )
