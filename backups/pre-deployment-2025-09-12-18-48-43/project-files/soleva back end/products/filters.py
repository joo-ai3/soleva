import django_filters
from django.db import models
from .models import Product, Category, Brand


class ProductFilter(django_filters.FilterSet):
    """Product filter set"""
    
    # Price range filters
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Category filters
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.filter(is_active=True))
    category_slug = django_filters.CharFilter(field_name='category__slug', lookup_expr='exact')
    
    # Brand filters
    brand = django_filters.ModelChoiceFilter(queryset=Brand.objects.filter(is_active=True))
    brand_slug = django_filters.CharFilter(field_name='brand__slug', lookup_expr='exact')
    
    # Boolean filters
    is_featured = django_filters.BooleanFilter(field_name='is_featured')
    is_on_sale = django_filters.BooleanFilter(method='filter_on_sale')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    is_digital = django_filters.BooleanFilter(field_name='is_digital')
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Search filter
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Product
        fields = [
            'category', 'brand', 'is_featured', 'is_digital',
            'min_price', 'max_price', 'category_slug', 'brand_slug'
        ]
    
    def filter_on_sale(self, queryset, name, value):
        """Filter products on sale"""
        if value:
            return queryset.filter(
                compare_price__isnull=False,
                compare_price__gt=models.F('price')
            )
        return queryset
    
    def filter_in_stock(self, queryset, name, value):
        """Filter products in stock"""
        if value:
            return queryset.filter(
                models.Q(track_inventory=False) |
                models.Q(track_inventory=True, inventory_quantity__gt=0)
            )
        return queryset
    
    def filter_search(self, queryset, name, value):
        """Search filter"""
        if value:
            return queryset.filter(
                models.Q(name_en__icontains=value) |
                models.Q(name_ar__icontains=value) |
                models.Q(description_en__icontains=value) |
                models.Q(description_ar__icontains=value) |
                models.Q(sku__icontains=value)
            )
        return queryset
