from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator
import uuid


class WebsiteSection(models.Model):
    """Model for managing website sections like banners, hero sections, etc."""
    
    SECTION_TYPES = [
        ('hero_banner', _('Hero Banner')),
        ('flash_sale_banner', _('Flash Sale Banner')),
        ('featured_products', _('Featured Products')),
        ('brand_story', _('Brand Story')),
        ('testimonials', _('Testimonials')),
        ('newsletter', _('Newsletter Section')),
        ('social_media', _('Social Media Section')),
        ('announcement_bar', _('Announcement Bar')),
        ('about_us', _('About Us Section')),
        ('contact_info', _('Contact Information')),
        ('footer_content', _('Footer Content')),
        ('custom', _('Custom Section')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Section Name'), max_length=100)
    section_type = models.CharField(_('Section Type'), max_length=50, choices=SECTION_TYPES)
    
    # Content fields
    title_en = models.CharField(_('Title (English)'), max_length=200, blank=True)
    title_ar = models.CharField(_('Title (Arabic)'), max_length=200, blank=True)
    subtitle_en = models.TextField(_('Subtitle (English)'), blank=True)
    subtitle_ar = models.TextField(_('Subtitle (Arabic)'), blank=True)
    content_en = models.TextField(_('Content (English)'), blank=True)
    content_ar = models.TextField(_('Content (Arabic)'), blank=True)
    
    # Media fields
    image = models.ImageField(_('Image'), upload_to='website_sections/', blank=True, null=True)
    background_image = models.ImageField(_('Background Image'), upload_to='website_sections/backgrounds/', blank=True, null=True)
    video_url = models.URLField(_('Video URL'), blank=True, validators=[URLValidator()])
    
    # CTA (Call to Action) fields
    cta_text_en = models.CharField(_('CTA Text (English)'), max_length=50, blank=True)
    cta_text_ar = models.CharField(_('CTA Text (Arabic)'), max_length=50, blank=True)
    cta_url = models.URLField(_('CTA URL'), blank=True)
    
    # Display settings
    is_active = models.BooleanField(_('Is Active'), default=True)
    display_order = models.PositiveIntegerField(_('Display Order'), default=0)
    
    # Style settings
    background_color = models.CharField(_('Background Color'), max_length=7, blank=True, help_text=_('Hex color code (e.g., #ffffff)'))
    text_color = models.CharField(_('Text Color'), max_length=7, blank=True, help_text=_('Hex color code (e.g., #000000)'))
    custom_css = models.TextField(_('Custom CSS'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Website Section')
        verbose_name_plural = _('Website Sections')
        ordering = ['display_order', 'created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_section_type_display()})"


class SiteConfiguration(models.Model):
    """Model for managing site-wide configuration settings"""
    
    # Site information
    site_name_en = models.CharField(_('Site Name (English)'), max_length=100, default='Soleva')
    site_name_ar = models.CharField(_('Site Name (Arabic)'), max_length=100, default='سوليفا')
    site_description_en = models.TextField(_('Site Description (English)'), blank=True)
    site_description_ar = models.TextField(_('Site Description (Arabic)'), blank=True)
    
    # Contact information
    primary_email = models.EmailField(_('Primary Email'), default='info@solevaeg.com')
    support_email = models.EmailField(_('Support Email'), default='support@solevaeg.com')
    sales_email = models.EmailField(_('Sales Email'), default='sales@solevaeg.com')
    business_email = models.EmailField(_('Business Email'), default='business@solevaeg.com')
    
    phone_number = models.CharField(_('Phone Number'), max_length=20, blank=True)
    whatsapp_number = models.CharField(_('WhatsApp Number'), max_length=20, blank=True)
    
    # Address
    address_en = models.TextField(_('Address (English)'), blank=True)
    address_ar = models.TextField(_('Address (Arabic)'), blank=True)
    
    # Social media
    facebook_url = models.URLField(_('Facebook URL'), default='https://www.facebook.com/share/1BNS1QbzkP/', blank=True)
    instagram_url = models.URLField(_('Instagram URL'), blank=True)
    twitter_url = models.URLField(_('Twitter URL'), blank=True)
    youtube_url = models.URLField(_('YouTube URL'), blank=True)
    tiktok_url = models.URLField(_('TikTok URL'), blank=True)
    
    # SEO settings
    meta_keywords_en = models.TextField(_('Meta Keywords (English)'), blank=True)
    meta_keywords_ar = models.TextField(_('Meta Keywords (Arabic)'), blank=True)
    google_analytics_id = models.CharField(_('Google Analytics ID'), max_length=50, blank=True)
    facebook_pixel_id = models.CharField(_('Facebook Pixel ID'), max_length=50, blank=True)
    
    # Business settings
    business_hours = models.TextField(_('Business Hours'), blank=True)
    shipping_info_en = models.TextField(_('Shipping Information (English)'), blank=True)
    shipping_info_ar = models.TextField(_('Shipping Information (Arabic)'), blank=True)
    return_policy_en = models.TextField(_('Return Policy (English)'), blank=True)
    return_policy_ar = models.TextField(_('Return Policy (Arabic)'), blank=True)
    
    # Maintenance mode
    maintenance_mode = models.BooleanField(_('Maintenance Mode'), default=False)
    maintenance_message_en = models.TextField(_('Maintenance Message (English)'), blank=True)
    maintenance_message_ar = models.TextField(_('Maintenance Message (Arabic)'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Site Configuration')
        verbose_name_plural = _('Site Configuration')
    
    def __str__(self):
        return f"Site Configuration - {self.site_name_en}"
    
    def save(self, *args, **kwargs):
        # Ensure only one configuration instance exists
        if not self.pk and SiteConfiguration.objects.exists():
            raise ValueError(_('Only one site configuration instance is allowed'))
        super().save(*args, **kwargs)


class NotificationBanner(models.Model):
    """Model for managing notification banners across the website"""
    
    BANNER_TYPES = [
        ('info', _('Information')),
        ('warning', _('Warning')),
        ('success', _('Success')),
        ('error', _('Error')),
        ('promotion', _('Promotion')),
        ('flash_sale', _('Flash Sale')),
        ('announcement', _('Announcement')),
    ]
    
    DISPLAY_LOCATIONS = [
        ('top', _('Top of Page')),
        ('header', _('Header')),
        ('footer', _('Footer')),
        ('sidebar', _('Sidebar')),
        ('popup', _('Popup')),
        ('all_pages', _('All Pages')),
        ('homepage', _('Homepage Only')),
        ('product_pages', _('Product Pages Only')),
        ('checkout', _('Checkout Only')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Banner Title'), max_length=100)
    message_en = models.TextField(_('Message (English)'))
    message_ar = models.TextField(_('Message (Arabic)'))
    
    banner_type = models.CharField(_('Banner Type'), max_length=20, choices=BANNER_TYPES, default='info')
    display_location = models.CharField(_('Display Location'), max_length=20, choices=DISPLAY_LOCATIONS, default='top')
    
    # Display settings
    is_active = models.BooleanField(_('Is Active'), default=True)
    is_dismissible = models.BooleanField(_('Is Dismissible'), default=True)
    auto_hide_after = models.PositiveIntegerField(_('Auto Hide After (seconds)'), blank=True, null=True)
    
    # Scheduling
    start_date = models.DateTimeField(_('Start Date'), blank=True, null=True)
    end_date = models.DateTimeField(_('End Date'), blank=True, null=True)
    
    # Styling
    background_color = models.CharField(_('Background Color'), max_length=7, blank=True)
    text_color = models.CharField(_('Text Color'), max_length=7, blank=True)
    icon = models.CharField(_('Icon Class'), max_length=50, blank=True)
    
    # CTA
    cta_text_en = models.CharField(_('CTA Text (English)'), max_length=50, blank=True)
    cta_text_ar = models.CharField(_('CTA Text (Arabic)'), max_length=50, blank=True)
    cta_url = models.URLField(_('CTA URL'), blank=True)
    
    # Priority and ordering
    priority = models.PositiveIntegerField(_('Priority'), default=1, help_text=_('Higher numbers show first'))
    display_order = models.PositiveIntegerField(_('Display Order'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Notification Banner')
        verbose_name_plural = _('Notification Banners')
        ordering = ['-priority', 'display_order', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_banner_type_display()})"
    
    @property
    def is_scheduled_active(self):
        """Check if banner is active based on scheduling"""
        from django.utils import timezone
        now = timezone.now()
        
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True
    
    @property
    def should_display(self):
        """Check if banner should be displayed"""
        return self.is_active and self.is_scheduled_active


class UserMessage(models.Model):
    """Model for user inbox messages"""
    
    MESSAGE_TYPES = [
        ('promotion', _('Promotion')),
        ('flash_sale', _('Flash Sale')),
        ('order_update', _('Order Update')),
        ('support_reply', _('Support Reply')),
        ('welcome', _('Welcome Message')),
        ('newsletter', _('Newsletter')),
        ('announcement', _('Announcement')),
        ('system', _('System Message')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='messages')
    
    # Message content
    subject_en = models.CharField(_('Subject (English)'), max_length=200)
    subject_ar = models.CharField(_('Subject (Arabic)'), max_length=200)
    message_en = models.TextField(_('Message (English)'))
    message_ar = models.TextField(_('Message (Arabic)'))
    
    message_type = models.CharField(_('Message Type'), max_length=20, choices=MESSAGE_TYPES, default='system')
    
    # Status
    is_read = models.BooleanField(_('Is Read'), default=False)
    is_important = models.BooleanField(_('Is Important'), default=False)
    
    # Optional attachments or links
    attachment = models.FileField(_('Attachment'), upload_to='user_messages/', blank=True, null=True)
    action_url = models.URLField(_('Action URL'), blank=True, help_text=_('URL for call-to-action button'))
    action_text_en = models.CharField(_('Action Text (English)'), max_length=50, blank=True)
    action_text_ar = models.CharField(_('Action Text (Arabic)'), max_length=50, blank=True)
    
    # Related objects (optional)
    related_order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, blank=True, null=True)
    related_product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, blank=True, null=True)
    
    # Timestamps
    sent_at = models.DateTimeField(_('Sent At'), auto_now_add=True)
    read_at = models.DateTimeField(_('Read At'), blank=True, null=True)
    expires_at = models.DateTimeField(_('Expires At'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('User Message')
        verbose_name_plural = _('User Messages')
        ordering = ['-is_important', '-sent_at']
    
    def __str__(self):
        return f"{self.subject_en} - {self.user.email}"
    
    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
