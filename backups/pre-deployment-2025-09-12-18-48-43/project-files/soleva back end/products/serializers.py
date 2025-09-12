from rest_framework import serializers
from django.db.models import Avg, Count
from .models import (
    Category, Brand, Product, ProductImage, ProductAttribute,
    ProductAttributeValue, ProductVariant, ProductVariantAttribute
)


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    
    children = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name_en', 'name_ar', 'slug', 'description_en', 'description_ar',
            'parent', 'children', 'image', 'icon', 'display_order',
            'meta_title_en', 'meta_title_ar', 'meta_description_en', 'meta_description_ar',
            'is_active', 'is_featured', 'products_count', 'created_at'
        ]
        read_only_fields = ['slug', 'created_at']
    
    def get_children(self, obj):
        """Get child categories"""
        if hasattr(obj, 'children'):
            children = obj.children.filter(is_active=True).order_by('display_order')
            return CategorySerializer(children, many=True, context=self.context).data
        return []
    
    def get_products_count(self, obj):
        """Get active products count"""
        return obj.products.filter(is_active=True).count()


class BrandSerializer(serializers.ModelSerializer):
    """Brand serializer"""
    
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'slug', 'description', 'logo', 'website',
            'is_active', 'is_featured', 'products_count', 'created_at'
        ]
        read_only_fields = ['slug', 'created_at']
    
    def get_products_count(self, obj):
        """Get active products count"""
        return obj.products.filter(is_active=True).count()


class ProductImageSerializer(serializers.ModelSerializer):
    """Product image serializer"""
    
    class Meta:
        model = ProductImage
        fields = [
            'id', 'image', 'alt_text_en', 'alt_text_ar', 
            'display_order', 'is_primary'
        ]


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    """Product attribute value serializer"""
    
    class Meta:
        model = ProductAttributeValue
        fields = [
            'id', 'value_en', 'value_ar', 'color_code', 'display_order'
        ]


class ProductAttributeSerializer(serializers.ModelSerializer):
    """Product attribute serializer"""
    
    values = ProductAttributeValueSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductAttribute
        fields = [
            'id', 'name_en', 'name_ar', 'slug', 'attribute_type',
            'is_required', 'is_filterable', 'display_order', 'values'
        ]


class ProductVariantAttributeSerializer(serializers.ModelSerializer):
    """Product variant attribute serializer"""
    
    attribute_name = serializers.CharField(source='attribute.name_en', read_only=True)
    value_name = serializers.CharField(source='value.value_en', read_only=True)
    
    class Meta:
        model = ProductVariantAttribute
        fields = ['attribute_name', 'value_name', 'attribute', 'value']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Product variant serializer"""
    
    attribute_values = ProductVariantAttributeSerializer(many=True, read_only=True)
    effective_price = serializers.ReadOnlyField()
    effective_compare_price = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'sku', 'price', 'compare_price', 'cost_price',
            'inventory_quantity', 'weight', 'image', 'is_active',
            'effective_price', 'effective_compare_price', 'is_in_stock',
            'attribute_values', 'created_at'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Product list serializer (minimal data)"""
    
    category_name = serializers.CharField(source='category.name_en', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    is_on_sale = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    variants_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name_en', 'name_ar', 'slug', 'sku', 'price', 'compare_price',
            'category_name', 'brand_name', 'primary_image', 'is_on_sale',
            'discount_percentage', 'is_in_stock', 'is_featured', 'variants_count',
            'created_at'
        ]
    
    def get_primary_image(self, obj):
        """Get primary product image"""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None
    
    def get_variants_count(self, obj):
        """Get active variants count"""
        return obj.variants.filter(is_active=True).count()


class ProductDetailSerializer(serializers.ModelSerializer):
    """Product detail serializer (complete data)"""
    
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    
    # Calculated fields
    is_on_sale = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    
    # Related data
    available_attributes = serializers.SerializerMethodField()
    related_products = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name_en', 'name_ar', 'slug', 'sku',
            'short_description_en', 'short_description_ar',
            'description_en', 'description_ar',
            'category', 'brand', 'price', 'compare_price',
            'track_inventory', 'inventory_quantity', 'low_stock_threshold',
            'weight', 'length', 'width', 'height',
            'meta_title_en', 'meta_title_ar', 'meta_description_en', 'meta_description_ar',
            'is_active', 'is_featured', 'is_digital', 'requires_shipping',
            'is_on_sale', 'discount_percentage', 'is_in_stock', 'is_low_stock',
            'images', 'variants', 'available_attributes', 'related_products',
            'created_at', 'updated_at', 'published_at'
        ]
    
    def get_available_attributes(self, obj):
        """Get available attributes for this product's variants"""
        # Get all attributes used by this product's variants
        variant_attributes = ProductVariantAttribute.objects.filter(
            variant__product=obj,
            variant__is_active=True
        ).select_related('attribute', 'value').order_by(
            'attribute__display_order', 'value__display_order'
        )
        
        # Group by attribute
        attributes_dict = {}
        for va in variant_attributes:
            attr_id = va.attribute.id
            if attr_id not in attributes_dict:
                attributes_dict[attr_id] = {
                    'id': va.attribute.id,
                    'name_en': va.attribute.name_en,
                    'name_ar': va.attribute.name_ar,
                    'attribute_type': va.attribute.attribute_type,
                    'values': []
                }
            
            value_data = {
                'id': va.value.id,
                'value_en': va.value.value_en,
                'value_ar': va.value.value_ar,
                'color_code': va.value.color_code
            }
            
            if value_data not in attributes_dict[attr_id]['values']:
                attributes_dict[attr_id]['values'].append(value_data)
        
        return list(attributes_dict.values())
    
    def get_related_products(self, obj):
        """Get related products from same category"""
        related = Product.objects.filter(
            category=obj.category,
            is_active=True
        ).exclude(id=obj.id)[:4]
        
        return ProductListSerializer(
            related, 
            many=True, 
            context=self.context
        ).data


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Product create/update serializer"""
    
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'name_en', 'name_ar', 'short_description_en', 'short_description_ar',
            'description_en', 'description_ar', 'category', 'brand',
            'price', 'compare_price', 'cost_price', 'track_inventory',
            'inventory_quantity', 'low_stock_threshold', 'weight',
            'length', 'width', 'height', 'meta_title_en', 'meta_title_ar',
            'meta_description_en', 'meta_description_ar', 'is_active',
            'is_featured', 'is_digital', 'requires_shipping', 'display_order',
            'images'
        ]
    
    def validate(self, attrs):
        """Custom validation"""
        if attrs.get('compare_price') and attrs.get('price'):
            if attrs['compare_price'] <= attrs['price']:
                raise serializers.ValidationError({
                    'compare_price': 'Compare price must be higher than regular price.'
                })
        return attrs


class ProductSearchSerializer(serializers.Serializer):
    """Product search parameters serializer"""
    
    q = serializers.CharField(required=False, help_text="Search query")
    category = serializers.IntegerField(required=False, help_text="Category ID")
    brand = serializers.IntegerField(required=False, help_text="Brand ID")
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    on_sale = serializers.BooleanField(required=False, help_text="Products on sale only")
    in_stock = serializers.BooleanField(required=False, help_text="In stock products only")
    featured = serializers.BooleanField(required=False, help_text="Featured products only")
    sort_by = serializers.ChoiceField(
        choices=[
            ('created_at', 'Newest'),
            ('-created_at', 'Oldest'),
            ('price', 'Price: Low to High'),
            ('-price', 'Price: High to Low'),
            ('name_en', 'Name: A to Z'),
            ('-name_en', 'Name: Z to A'),
        ],
        required=False,
        default='-created_at'
    )
