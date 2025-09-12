from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class Cart(models.Model):
    """Shopping cart for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    session_key = models.CharField(_('session key'), max_length=40, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
        db_table = 'shopping_carts'
    
    def __str__(self):
        return f"Cart for {self.user.email if self.user else self.session_key}"
    
    @property
    def total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        """Get cart subtotal"""
        return sum(item.total_price for item in self.items.all())
    
    def clear(self):
        """Clear all items from cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """Individual items in shopping cart"""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_id = models.PositiveIntegerField(_('product ID'))
    variant_id = models.PositiveIntegerField(_('variant ID'), blank=True, null=True)
    quantity = models.PositiveIntegerField(_('quantity'), default=1)
    
    # Store product details at time of adding to cart
    product_name = models.CharField(_('product name'), max_length=255)
    product_price = models.DecimalField(_('product price'), max_digits=10, decimal_places=2)
    product_image = models.URLField(_('product image'), blank=True)
    variant_attributes = models.JSONField(_('variant attributes'), default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        db_table = 'cart_items'
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product_id', 'variant_id'],
                name='unique_cart_product_variant'
            ),
        ]
        indexes = [
            models.Index(fields=['cart']),
            models.Index(fields=['product_id']),
        ]
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    @property
    def total_price(self):
        """Get total price for this cart item"""
        return self.product_price * self.quantity


class SavedForLater(models.Model):
    """Items saved for later (wishlist)"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_items')
    product_id = models.PositiveIntegerField(_('product ID'))
    variant_id = models.PositiveIntegerField(_('variant ID'), blank=True, null=True)
    
    # Store product details
    product_name = models.CharField(_('product name'), max_length=255)
    product_price = models.DecimalField(_('product price'), max_digits=10, decimal_places=2)
    product_image = models.URLField(_('product image'), blank=True)
    variant_attributes = models.JSONField(_('variant attributes'), default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Saved for Later')
        verbose_name_plural = _('Saved for Later')
        db_table = 'saved_for_later'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product_id', 'variant_id'],
                name='unique_saved_product_variant'
            ),
        ]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['product_id']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.product_name}"
