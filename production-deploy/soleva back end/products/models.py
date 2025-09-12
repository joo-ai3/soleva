from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import uuid


class Category(models.Model):
    """Product categories with hierarchical structure"""
    
    name_en = models.CharField(_('name (English)'), max_length=100)
    name_ar = models.CharField(_('name (Arabic)'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=120, unique=True)
    description_en = models.TextField(_('description (English)'), blank=True)
    description_ar = models.TextField(_('description (Arabic)'), blank=True)
    
    # Hierarchical structure
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    
    # Display settings
    image = models.ImageField(_('image'), upload_to='categories/', blank=True, null=True)
    icon = models.CharField(_('icon class'), max_length=100, blank=True)
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    
    # SEO fields
    meta_title_en = models.CharField(_('meta title (English)'), max_length=60, blank=True)
    meta_title_ar = models.CharField(_('meta title (Arabic)'), max_length=60, blank=True)
    meta_description_en = models.TextField(_('meta description (English)'), max_length=160, blank=True)
    meta_description_ar = models.TextField(_('meta description (Arabic)'), max_length=160, blank=True)
    
    # Status
    is_active = models.BooleanField(_('is active'), default=True)
    is_featured = models.BooleanField(_('is featured'), default=False)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        db_table = 'product_categories'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'display_order']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return self.name_en
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)
    
    @property
    def level(self):
        """Get category hierarchy level"""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level


class Brand(models.Model):
    """Product brands"""
    
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=120, unique=True)
    description = models.TextField(_('description'), blank=True)
    logo = models.ImageField(_('logo'), upload_to='brands/', blank=True, null=True)
    website = models.URLField(_('website'), blank=True)
    
    # Status
    is_active = models.BooleanField(_('is active'), default=True)
    is_featured = models.BooleanField(_('is featured'), default=False)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')
        db_table = 'product_brands'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Main product model"""
    
    # Basic info
    name_en = models.CharField(_('name (English)'), max_length=255)
    name_ar = models.CharField(_('name (Arabic)'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=280, unique=True)
    sku = models.CharField(_('SKU'), max_length=100, unique=True)
    
    # Descriptions
    short_description_en = models.TextField(_('short description (English)'), max_length=500)
    short_description_ar = models.TextField(_('short description (Arabic)'), max_length=500)
    description_en = models.TextField(_('description (English)'))
    description_ar = models.TextField(_('description (Arabic)'))
    
    # Relationships
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    # Pricing
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(_('compare at price'), max_digits=10, decimal_places=2, blank=True, null=True)
    cost_price = models.DecimalField(_('cost price'), max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Inventory
    track_inventory = models.BooleanField(_('track inventory'), default=True)
    inventory_quantity = models.PositiveIntegerField(_('inventory quantity'), default=0)
    low_stock_threshold = models.PositiveIntegerField(_('low stock threshold'), default=5)
    
    # Physical attributes
    weight = models.DecimalField(_('weight (kg)'), max_digits=8, decimal_places=3, blank=True, null=True)
    length = models.DecimalField(_('length (cm)'), max_digits=8, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(_('width (cm)'), max_digits=8, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(_('height (cm)'), max_digits=8, decimal_places=2, blank=True, null=True)
    
    # SEO fields
    meta_title_en = models.CharField(_('meta title (English)'), max_length=60, blank=True)
    meta_title_ar = models.CharField(_('meta title (Arabic)'), max_length=60, blank=True)
    meta_description_en = models.TextField(_('meta description (English)'), max_length=160, blank=True)
    meta_description_ar = models.TextField(_('meta description (Arabic)'), max_length=160, blank=True)
    
    # Status and visibility
    is_active = models.BooleanField(_('is active'), default=True)
    is_featured = models.BooleanField(_('is featured'), default=False)
    is_digital = models.BooleanField(_('is digital'), default=False)
    requires_shipping = models.BooleanField(_('requires shipping'), default=True)
    
    # Display settings
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    published_at = models.DateTimeField(_('published at'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        db_table = 'products'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['created_at']),
            models.Index(fields=['price']),
        ]
    
    def __str__(self):
        return self.name_en
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        if not self.sku:
            self.sku = f"SOL-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def is_on_sale(self):
        """Check if product is on sale"""
        return self.compare_price and self.compare_price > self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.is_on_sale:
            return round(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        if not self.track_inventory:
            return True
        return self.inventory_quantity > 0
    
    @property
    def is_low_stock(self):
        """Check if product is low in stock"""
        if not self.track_inventory:
            return False
        return self.inventory_quantity <= self.low_stock_threshold


class ProductImage(models.Model):
    """Product images"""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(_('image'), upload_to='products/')
    alt_text_en = models.CharField(_('alt text (English)'), max_length=255, blank=True)
    alt_text_ar = models.CharField(_('alt text (Arabic)'), max_length=255, blank=True)
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    is_primary = models.BooleanField(_('is primary'), default=False)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        db_table = 'product_images'
        indexes = [
            models.Index(fields=['product', 'display_order']),
            models.Index(fields=['product', 'is_primary']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['product'],
                condition=models.Q(is_primary=True),
                name='unique_primary_image_per_product'
            ),
        ]
    
    def __str__(self):
        return f"{self.product.name_en} - Image {self.display_order}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductAttribute(models.Model):
    """Product attributes (color, size, material, etc.)"""
    
    name_en = models.CharField(_('name (English)'), max_length=100)
    name_ar = models.CharField(_('name (Arabic)'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=120, unique=True)
    
    # Attribute type
    ATTRIBUTE_TYPES = [
        ('text', _('Text')),
        ('number', _('Number')),
        ('color', _('Color')),
        ('select', _('Select')),
        ('multiselect', _('Multi-select')),
    ]
    attribute_type = models.CharField(_('attribute type'), max_length=20, choices=ATTRIBUTE_TYPES, default='text')
    
    # Display settings
    is_required = models.BooleanField(_('is required'), default=False)
    is_filterable = models.BooleanField(_('is filterable'), default=True)
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Product Attribute')
        verbose_name_plural = _('Product Attributes')
        db_table = 'product_attributes'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['attribute_type']),
        ]
    
    def __str__(self):
        return self.name_en
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)


class ProductAttributeValue(models.Model):
    """Product attribute values"""
    
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='values')
    value_en = models.CharField(_('value (English)'), max_length=255)
    value_ar = models.CharField(_('value (Arabic)'), max_length=255)
    color_code = models.CharField(_('color code'), max_length=7, blank=True)  # For color attributes
    
    # Display settings
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Product Attribute Value')
        verbose_name_plural = _('Product Attribute Values')
        db_table = 'product_attribute_values'
        indexes = [
            models.Index(fields=['attribute', 'display_order']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['attribute', 'value_en'],
                name='unique_attribute_value_en'
            ),
        ]
    
    def __str__(self):
        return f"{self.attribute.name_en}: {self.value_en}"


class ProductVariant(models.Model):
    """Product variants (different combinations of attributes)"""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(_('SKU'), max_length=100, unique=True)
    
    # Pricing (can override product pricing)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2, blank=True, null=True)
    compare_price = models.DecimalField(_('compare at price'), max_digits=10, decimal_places=2, blank=True, null=True)
    cost_price = models.DecimalField(_('cost price'), max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Inventory
    inventory_quantity = models.PositiveIntegerField(_('inventory quantity'), default=0)
    
    # Physical attributes (can override product attributes)
    weight = models.DecimalField(_('weight (kg)'), max_digits=8, decimal_places=3, blank=True, null=True)
    
    # Images
    image = models.ImageField(_('variant image'), upload_to='variants/', blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Product Variant')
        verbose_name_plural = _('Product Variants')
        db_table = 'product_variants'
        indexes = [
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['sku']),
        ]
    
    def __str__(self):
        return f"{self.product.name_en} - {self.sku}"
    
    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"{self.product.sku}-{uuid.uuid4().hex[:4].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def effective_price(self):
        """Get effective price (variant price or product price)"""
        return self.price or self.product.price
    
    @property
    def effective_compare_price(self):
        """Get effective compare price"""
        return self.compare_price or self.product.compare_price
    
    @property
    def is_in_stock(self):
        """Check if variant is in stock"""
        return self.inventory_quantity > 0


class ProductVariantAttribute(models.Model):
    """Link variants to their attribute values"""
    
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='attribute_values')
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    value = models.ForeignKey(ProductAttributeValue, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = _('Product Variant Attribute')
        verbose_name_plural = _('Product Variant Attributes')
        db_table = 'product_variant_attributes'
        constraints = [
            models.UniqueConstraint(
                fields=['variant', 'attribute'],
                name='unique_variant_attribute'
            ),
        ]
    
    def __str__(self):
        return f"{self.variant.sku} - {self.attribute.name_en}: {self.value.value_en}"
