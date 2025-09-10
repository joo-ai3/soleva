#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soleva_backend.settings')

django.setup()

from django.conf import settings

print("=== Django Configuration Check ===")
print(f"DEBUG: {settings.DEBUG}")
print(f"SECRET_KEY: {'*' * len(settings.SECRET_KEY)} (length: {len(settings.SECRET_KEY)})")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print()

print("=== Database Configuration ===")
db_config = settings.DATABASES['default']
print(f"ENGINE: {db_config['ENGINE']}")
print(f"NAME: {db_config['NAME']}")
print(f"HOST: {db_config.get('HOST', 'Not set')}")
print(f"PORT: {db_config.get('PORT', 'Not set')}")
print(f"USER: {db_config.get('USER', 'Not set')}")
print(f"PASSWORD: {'*' * len(db_config.get('PASSWORD', ''))} (length: {len(db_config.get('PASSWORD', ''))})")
print()

print("=== Installed Apps ===")
for app in settings.INSTALLED_APPS:
    print(f"  - {app}")
print()

print("=== Middleware ===")
for middleware in settings.MIDDLEWARE:
    print(f"  - {middleware}")
print()

print("=== REST Framework Settings ===")
if hasattr(settings, 'REST_FRAMEWORK'):
    for key, value in settings.REST_FRAMEWORK.items():
        print(f"  {key}: {value}")
print()

print("Configuration check completed!")
