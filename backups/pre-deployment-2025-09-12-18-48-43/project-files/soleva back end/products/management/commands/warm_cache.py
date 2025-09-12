"""
Management command to warm up application caches
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from utils.cache import CacheWarmer
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Warm up application caches with frequently accessed data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['all', 'products', 'categories'],
            default='all',
            help='Type of cache to warm (default: all)'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
    
    def handle(self, *args, **options):
        start_time = timezone.now()
        cache_type = options['type']
        verbose = options['verbose']
        
        if verbose:
            self.stdout.write(f"Starting cache warming at {start_time}")
        
        try:
            if cache_type == 'all':
                CacheWarmer.warm_all_caches()
                self.stdout.write(
                    self.style.SUCCESS('Successfully warmed all caches')
                )
            elif cache_type == 'products':
                CacheWarmer.warm_product_cache()
                self.stdout.write(
                    self.style.SUCCESS('Successfully warmed product cache')
                )
            elif cache_type == 'categories':
                CacheWarmer.warm_category_cache()
                self.stdout.write(
                    self.style.SUCCESS('Successfully warmed category cache')
                )
            
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            
            if verbose:
                self.stdout.write(f"Cache warming completed in {duration:.2f} seconds")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to warm cache: {str(e)}')
            )
            logger.error(f"Cache warming failed: {e}", exc_info=True)
