#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'soleva_backend.settings'
    django.setup()

    # Test basic Django functionality
    from django.urls import reverse
    print("Django setup successful")

    # Test if we can import the health view
    try:
        from soleva_backend.urls import health_check
        print("Health check view imported successfully")
    except Exception as e:
        print(f"Error importing health check: {e}")

    # Test URL resolution
    try:
        from django.urls import resolve
        match = resolve('/api/health/')
        print(f"URL resolution successful: {match}")
    except Exception as e:
        print(f"URL resolution failed: {e}")
