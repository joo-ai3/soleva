#!/usr/bin/env python
"""
Health check endpoint for Django backend
Used by Docker health checks and load balancers
"""

import os
import django
from django.conf import settings
from django.http import JsonResponse
from django.core.management import execute_from_command_line

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soleva_backend.settings')
django.setup()

def health_check():
    """Perform health checks and return status"""
    from django.db import connection
    from django.core.cache import cache
    import redis
    
    health_status = {
        'status': 'healthy',
        'timestamp': django.utils.timezone.now().isoformat(),
        'checks': {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Redis/Cache check
    try:
        cache.set('health_check', 'ok', 30)
        cache.get('health_check')
        health_status['checks']['cache'] = 'healthy'
    except Exception as e:
        health_status['checks']['cache'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Celery broker check (Redis)
    try:
        from celery import current_app
        inspect = current_app.control.inspect()
        stats = inspect.stats()
        if stats:
            health_status['checks']['celery'] = 'healthy'
        else:
            health_status['checks']['celery'] = 'no workers'
    except Exception as e:
        health_status['checks']['celery'] = f'unhealthy: {str(e)}'
    
    return health_status

if __name__ == '__main__':
    # This can be run as a standalone script
    import json
    status = health_check()
    print(json.dumps(status, indent=2))
    
    # Exit with error code if unhealthy
    if status['status'] != 'healthy':
        exit(1)
