from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserMessage, SiteConfiguration

User = get_user_model()


@receiver(post_save, sender=User)
def create_welcome_message(sender, instance, created, **kwargs):
    """Create a welcome message for new users"""
    if created and not instance.is_staff:
        UserMessage.objects.create(
            user=instance,
            subject_en="Welcome to Soleva!",
            subject_ar="مرحباً بك في سوليفا!",
            message_en="""Welcome to Soleva! We're excited to have you join our community.

Discover our exclusive collection of premium products and enjoy:
• Premium quality items
• Fast and reliable shipping
• Excellent customer service
• Special offers and promotions

Start exploring our collection and find your perfect style!""",
            message_ar="""مرحباً بك في سوليفا! نحن متحمسون لانضمامك إلى مجتمعنا.

اكتشف مجموعتنا الحصرية من المنتجات المميزة واستمتع بـ:
• منتجات عالية الجودة
• شحن سريع وموثوق
• خدمة عملاء ممتازة
• عروض وتخفيضات خاصة

ابدأ في استكشاف مجموعتنا واعثر على أسلوبك المثالي!""",
            message_type='welcome',
            is_important=True
        )


@receiver(post_save, sender=SiteConfiguration)
def update_site_config_cache(sender, instance, **kwargs):
    """Clear cache when site configuration is updated"""
    from django.core.cache import cache
    cache.delete('site_configuration')
    cache.delete('site_config_public')
