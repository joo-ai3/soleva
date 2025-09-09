"""
Enhanced caching utilities for Soleva platform
"""
import json
import logging
from typing import Any, Optional, Union, Callable
from functools import wraps
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.utils.encoding import force_str
import hashlib

logger = logging.getLogger(__name__)

# Cache timeouts (in seconds)
CACHE_TIMEOUTS = {
    'short': 300,      # 5 minutes
    'medium': 3600,    # 1 hour
    'long': 86400,     # 24 hours
    'extra_long': 604800,  # 1 week
}

class CacheManager:
    """Enhanced cache manager with compression and serialization"""
    
    @staticmethod
    def generate_cache_key(prefix: str, *args, **kwargs) -> str:
        """Generate a unique cache key from arguments"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        key_string = json.dumps(key_data, cls=DjangoJSONEncoder, sort_keys=True)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    @staticmethod
    def set_cache(key: str, value: Any, timeout: Union[int, str] = 'medium') -> bool:
        """Set cache value with optional compression"""
        try:
            if isinstance(timeout, str):
                timeout = CACHE_TIMEOUTS.get(timeout, CACHE_TIMEOUTS['medium'])
            
            # Serialize complex objects
            if not isinstance(value, (str, int, float, bool, type(None))):
                value = json.dumps(value, cls=DjangoJSONEncoder)
                key = f"json:{key}"
            
            cache.set(key, value, timeout)
            logger.debug(f"Cache set: {key} (timeout: {timeout}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    @staticmethod
    def get_cache(key: str, default: Any = None) -> Any:
        """Get cache value with automatic deserialization"""
        try:
            value = cache.get(key)
            if value is None:
                return default
            
            # Deserialize JSON objects
            if key.startswith("json:"):
                key = key[5:]  # Remove json: prefix
                value = cache.get(f"json:{key}")
                if value is not None:
                    return json.loads(value)
            
            logger.debug(f"Cache hit: {key}")
            return value
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default
    
    @staticmethod
    def delete_cache(key: str) -> bool:
        """Delete cache key"""
        try:
            cache.delete(key)
            cache.delete(f"json:{key}")  # Also try to delete JSON version
            logger.debug(f"Cache deleted: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    @staticmethod
    def clear_pattern(pattern: str) -> bool:
        """Clear cache keys matching pattern (Redis only)"""
        try:
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(f"*{pattern}*")
                logger.debug(f"Cache pattern cleared: {pattern}")
                return True
            else:
                logger.warning("Cache backend doesn't support pattern deletion")
                return False
        except Exception as e:
            logger.error(f"Cache pattern clear error for {pattern}: {e}")
            return False

def cache_result(timeout: Union[int, str] = 'medium', key_prefix: str = None):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = CacheManager.generate_cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            result = CacheManager.get_cache(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            CacheManager.set_cache(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """Decorator to invalidate cache patterns after function execution"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            CacheManager.clear_pattern(pattern)
            return result
        return wrapper
    return decorator

# Specific cache utilities for different models
class ProductCache:
    """Product-specific caching utilities"""
    
    @staticmethod
    @cache_result(timeout='long', key_prefix='product_detail')
    def get_product_detail(product_id: int):
        """Cache product detail with relationships"""
        from products.models import Product
        try:
            return Product.objects.select_related(
                'category', 'brand'
            ).prefetch_related(
                'images', 'variants', 'attributes'
            ).get(id=product_id)
        except Product.DoesNotExist:
            return None
    
    @staticmethod
    @cache_result(timeout='medium', key_prefix='product_list')
    def get_product_list(category_id: int = None, brand_id: int = None, limit: int = 20):
        """Cache product listings"""
        from products.models import Product
        queryset = Product.objects.filter(is_active=True)
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)
        
        return list(queryset.select_related('category', 'brand')[:limit])
    
    @staticmethod
    def invalidate_product_cache(product_id: int):
        """Invalidate product-related caches"""
        CacheManager.clear_pattern(f"product_detail:{product_id}")
        CacheManager.clear_pattern("product_list")

class CategoryCache:
    """Category-specific caching utilities"""
    
    @staticmethod
    @cache_result(timeout='extra_long', key_prefix='category_tree')
    def get_category_tree():
        """Cache category hierarchy"""
        from products.models import Category
        return list(Category.objects.filter(is_active=True).order_by('name'))
    
    @staticmethod
    def invalidate_category_cache():
        """Invalidate category caches"""
        CacheManager.clear_pattern("category_tree")
        CacheManager.clear_pattern("product_list")  # Products are affected too

class CartCache:
    """Cart-specific caching utilities"""
    
    @staticmethod
    def get_cart_key(user_id: int) -> str:
        """Generate cart cache key for user"""
        return f"cart:user:{user_id}"
    
    @staticmethod
    def set_cart(user_id: int, cart_data: dict):
        """Cache user's cart data"""
        cache_key = CartCache.get_cart_key(user_id)
        CacheManager.set_cache(cache_key, cart_data, timeout='short')
    
    @staticmethod
    def get_cart(user_id: int):
        """Get cached cart data"""
        cache_key = CartCache.get_cart_key(user_id)
        return CacheManager.get_cache(cache_key)
    
    @staticmethod
    def invalidate_cart(user_id: int):
        """Invalidate user's cart cache"""
        cache_key = CartCache.get_cart_key(user_id)
        CacheManager.delete_cache(cache_key)

# Session-based caching for anonymous users
class SessionCache:
    """Session-based caching for guest users"""
    
    @staticmethod
    def get_session_key(session_key: str, prefix: str) -> str:
        """Generate session-based cache key"""
        return f"session:{prefix}:{session_key}"
    
    @staticmethod
    def set_session_data(session_key: str, prefix: str, data: Any, timeout: Union[int, str] = 'short'):
        """Cache session data"""
        cache_key = SessionCache.get_session_key(session_key, prefix)
        CacheManager.set_cache(cache_key, data, timeout)
    
    @staticmethod
    def get_session_data(session_key: str, prefix: str, default: Any = None):
        """Get session data"""
        cache_key = SessionCache.get_session_key(session_key, prefix)
        return CacheManager.get_cache(cache_key, default)
    
    @staticmethod
    def invalidate_session_data(session_key: str, prefix: str):
        """Invalidate session data"""
        cache_key = SessionCache.get_session_key(session_key, prefix)
        CacheManager.delete_cache(cache_key)

# Cache warming utilities
class CacheWarmer:
    """Utilities to pre-warm cache with important data"""
    
    @staticmethod
    def warm_product_cache():
        """Pre-warm product cache with popular items"""
        try:
            from products.models import Product
            popular_products = Product.objects.filter(
                is_active=True
            ).order_by('-view_count', '-created_at')[:50]
            
            for product in popular_products:
                ProductCache.get_product_detail(product.id)
            
            logger.info("Product cache warmed successfully")
        except Exception as e:
            logger.error(f"Product cache warming failed: {e}")
    
    @staticmethod
    def warm_category_cache():
        """Pre-warm category cache"""
        try:
            CategoryCache.get_category_tree()
            logger.info("Category cache warmed successfully")
        except Exception as e:
            logger.error(f"Category cache warming failed: {e}")
    
    @staticmethod
    def warm_all_caches():
        """Warm all important caches"""
        CacheWarmer.warm_category_cache()
        CacheWarmer.warm_product_cache()
        logger.info("All caches warmed successfully")

# Management command utility
def clear_all_caches():
    """Clear all application caches"""
    try:
        cache.clear()
        logger.info("All caches cleared successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to clear caches: {e}")
        return False