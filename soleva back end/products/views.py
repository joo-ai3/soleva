from rest_framework import status, permissions, filters, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django.db.models import Q, Count, Avg, Min, Max
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from fuzzywuzzy import fuzz, process

from .models import Category, Brand, Product, ProductImage, ProductAttribute
from .serializers import (
    CategorySerializer, BrandSerializer, ProductListSerializer,
    ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductSearchSerializer, ProductAttributeSerializer
)
from .filters import ProductFilter


class CategoryViewSet(ReadOnlyModelViewSet):
    """Category viewset"""
    
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['parent', 'is_featured']
    ordering_fields = ['display_order', 'name_en', 'created_at']
    ordering = ['display_order', 'name_en']
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Get active categories"""
        return Category.objects.filter(is_active=True).prefetch_related('children')
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category tree structure"""
        cache_key = 'category_tree'
        tree_data = cache.get(cache_key)
        
        if not tree_data:
            # Get root categories (no parent)
            root_categories = self.get_queryset().filter(parent=None)
            tree_data = CategorySerializer(
                root_categories, 
                many=True, 
                context={'request': request}
            ).data
            
            # Cache for 1 hour
            cache.set(cache_key, tree_data, 3600)
        
        return Response(tree_data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured categories"""
        featured_categories = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured_categories, many=True)
        return Response(serializer.data)


class BrandViewSet(ReadOnlyModelViewSet):
    """Brand viewset"""
    
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Get active brands"""
        return Brand.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured brands"""
        featured_brands = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured_brands, many=True)
        return Response(serializer.data)


class ProductViewSet(ModelViewSet):
    """Product viewset"""
    
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name_en', 'name_ar', 'description_en', 'description_ar', 'sku']
    ordering_fields = ['created_at', 'price', 'name_en', 'display_order']
    ordering = ['-created_at']
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Get products queryset"""
        queryset = Product.objects.filter(is_active=True).select_related(
            'category', 'brand'
        ).prefetch_related('images', 'variants')
        
        return queryset
    
    def get_serializer_class(self):
        """Get appropriate serializer class"""
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer
    
    def get_permissions(self):
        """Get permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        featured_products = self.get_queryset().filter(is_featured=True)[:12]
        serializer = ProductListSerializer(
            featured_products, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        """Get products on sale"""
        on_sale_products = self.get_queryset().filter(
            compare_price__isnull=False,
            compare_price__gt=models.F('price')
        )[:12]
        
        serializer = ProductListSerializer(
            on_sale_products, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        """Get new arrival products"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Products added in the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        new_products = self.get_queryset().filter(
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:12]
        
        serializer = ProductListSerializer(
            new_products, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def related(self, request, slug=None):
        """Get related products"""
        product = self.get_object()
        
        # Get products from same category, excluding current product
        related_products = self.get_queryset().filter(
            category=product.category
        ).exclude(id=product.id)[:6]
        
        serializer = ProductListSerializer(
            related_products, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Advanced product search with fuzzy matching"""
        search_serializer = ProductSearchSerializer(data=request.data)
        if not search_serializer.is_valid():
            return Response(search_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = search_serializer.validated_data
        queryset = self.get_queryset()
        
        # Text search with fuzzy matching
        if data.get('q'):
            query = data['q']
            
            # First, try exact matches
            exact_matches = queryset.filter(
                Q(name_en__icontains=query) |
                Q(name_ar__icontains=query) |
                Q(description_en__icontains=query) |
                Q(description_ar__icontains=query) |
                Q(sku__icontains=query)
            )
            
            # If no exact matches, try fuzzy search
            if not exact_matches.exists():
                all_products = list(queryset.values('id', 'name_en', 'name_ar'))
                
                # Create search corpus
                search_corpus = []
                product_map = {}
                for product in all_products:
                    search_text = f"{product['name_en']} {product['name_ar']}"
                    search_corpus.append(search_text)
                    product_map[search_text] = product['id']
                
                # Fuzzy search
                matches = process.extract(query, search_corpus, limit=20)
                fuzzy_product_ids = [
                    product_map[match[0]] 
                    for match in matches 
                    if match[1] > 60  # 60% similarity threshold
                ]
                
                queryset = queryset.filter(id__in=fuzzy_product_ids)
            else:
                queryset = exact_matches
        
        # Apply filters
        if data.get('category'):
            queryset = queryset.filter(category_id=data['category'])
        
        if data.get('brand'):
            queryset = queryset.filter(brand_id=data['brand'])
        
        if data.get('min_price'):
            queryset = queryset.filter(price__gte=data['min_price'])
        
        if data.get('max_price'):
            queryset = queryset.filter(price__lte=data['max_price'])
        
        if data.get('on_sale'):
            queryset = queryset.filter(
                compare_price__isnull=False,
                compare_price__gt=models.F('price')
            )
        
        if data.get('in_stock'):
            queryset = queryset.filter(
                Q(track_inventory=False) |
                Q(track_inventory=True, inventory_quantity__gt=0)
            )
        
        if data.get('featured'):
            queryset = queryset.filter(is_featured=True)
        
        # Apply sorting
        sort_by = data.get('sort_by', '-created_at')
        queryset = queryset.order_by(sort_by)
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(
                page, 
                many=True, 
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(
            queryset, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)


class ProductAttributeViewSet(ReadOnlyModelViewSet):
    """Product attribute viewset"""
    
    serializer_class = ProductAttributeSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['display_order', 'name_en']
    ordering = ['display_order', 'name_en']
    
    def get_queryset(self):
        """Get filterable attributes"""
        return ProductAttribute.objects.filter(is_filterable=True).prefetch_related('values')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def product_stats(request):
    """Get product statistics"""
    cache_key = 'product_stats'
    stats = cache.get(cache_key)
    
    if not stats:
        products = Product.objects.filter(is_active=True)
        
        stats = {
            'total_products': products.count(),
            'total_categories': Category.objects.filter(is_active=True).count(),
            'total_brands': Brand.objects.filter(is_active=True).count(),
            'featured_products': products.filter(is_featured=True).count(),
            'products_on_sale': products.filter(
                compare_price__isnull=False,
                compare_price__gt=models.F('price')
            ).count(),
            'price_range': products.aggregate(
                min_price=Min('price'),
                max_price=Max('price')
            ),
            'average_price': products.aggregate(avg_price=Avg('price'))['avg_price'],
        }
        
        # Cache for 30 minutes
        cache.set(cache_key, stats, 1800)
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_suggestions(request):
    """Get search suggestions"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return Response([])
    
    # Search in product names and categories
    products = Product.objects.filter(
        Q(name_en__icontains=query) | Q(name_ar__icontains=query),
        is_active=True
    ).values('name_en', 'name_ar', 'slug')[:5]
    
    categories = Category.objects.filter(
        Q(name_en__icontains=query) | Q(name_ar__icontains=query),
        is_active=True
    ).values('name_en', 'name_ar', 'slug')[:3]
    
    brands = Brand.objects.filter(
        name__icontains=query,
        is_active=True
    ).values('name', 'slug')[:3]
    
    suggestions = {
        'products': list(products),
        'categories': list(categories),
        'brands': list(brands)
    }
    
    return Response(suggestions)
