"""
Production-ready Django settings for soleva_backend
"""

import os
from pathlib import Path
from datetime import timedelta

# Try to import decouple, fallback to os.environ if not available
try:
    from decouple import config
except ImportError:
    def config(key, default=None, cast=str):
        value = os.environ.get(key, default)
        if cast != str and value is not None:
            if cast == bool:
                return str(value).lower() in ('true', '1', 'yes', 'on')
            elif cast == list:
                return [item.strip() for item in str(value).split(',')]
            else:
                return cast(value)
        return value

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='change-this-in-production')
DEBUG = config('DEBUG', default=False, cast=bool)

# Configure ALLOWED_HOSTS
ALLOWED_HOSTS_ENV = config('ALLOWED_HOSTS', default='')
print(f"DEBUG: ALLOWED_HOSTS_ENV = '{ALLOWED_HOSTS_ENV}'")  # Debug logging

if ALLOWED_HOSTS_ENV:
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_ENV.split(',')]
    print(f"DEBUG: ALLOWED_HOSTS from env = {ALLOWED_HOSTS}")  # Debug logging
else:
    ALLOWED_HOSTS = [
        'solevaeg.com',
        'www.solevaeg.com',
        '213.130.147.41',
        'backend',          # Docker service name for inter-container communication
        'backend:8000',     # Docker service with port for inter-container communication
        'frontend',         # Docker service name
        'nginx',            # Docker service name
        'localhost',        # For local development
        '127.0.0.1',       # For local development
        '0.0.0.0',         # For Docker containers
    ]
    print(f"DEBUG: ALLOWED_HOSTS using defaults = {ALLOWED_HOSTS}")  # Debug logging

# Add additional hosts from environment if specified
EXTRA_ALLOWED_HOSTS = config('EXTRA_ALLOWED_HOSTS', default='')
if EXTRA_ALLOWED_HOSTS:
    extra_hosts = [host.strip() for host in EXTRA_ALLOWED_HOSTS.split(',')]
    ALLOWED_HOSTS.extend(extra_hosts)
    print(f"DEBUG: Added EXTRA_ALLOWED_HOSTS = {extra_hosts}")  # Debug logging

# Remove duplicates and filter out empty strings
ALLOWED_HOSTS = list(set(filter(None, ALLOWED_HOSTS)))
print(f"DEBUG: FINAL ALLOWED_HOSTS = {ALLOWED_HOSTS}")  # Debug logging

# Sentry
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN and not DEBUG:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                DjangoIntegration(
                    transaction_style='url',
                    middleware_spans=False,
                    signals_denylist=[
                        'django.db.models.signals.pre_save',
                        'django.db.models.signals.post_save',
                    ]
                ),
                CeleryIntegration(monitor_beat_tasks=True),
            ],
            traces_sample_rate=0.1,
            send_default_pii=False,
            attach_stacktrace=True,
            environment='production',
        )
        print("Sentry initialized successfully")
    except ImportError as e:
        print(f"Sentry SDK not available: {e}")
    except Exception as e:
        print(f"Sentry initialization failed: {e}")

# Apps
DJANGO_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework','rest_framework_simplejwt','corsheaders','django_filters','django_celery_beat',
]

LOCAL_APPS = [
    'users','products','orders','cart','coupons','notifications','accounting',
    'shipping','payments','tracking','offers','otp','website_management',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'soleva_backend.urls'

TEMPLATES = [
    {'BACKEND':'django.template.backends.django.DjangoTemplates',
     'DIRS':[BASE_DIR / 'templates'],
     'APP_DIRS': True,
     'OPTIONS':{'context_processors':[
         'django.template.context_processors.debug',
         'django.template.context_processors.request',
         'django.contrib.auth.context_processors.auth',
         'django.contrib.messages.context_processors.messages',
     ]},
    },
]

WSGI_APPLICATION = 'soleva_backend.wsgi.application'

# Database Configuration
USE_SQLITE = config('USE_SQLITE', default=False, cast=bool)

if USE_SQLITE:
    # SQLite for local development/testing
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # PostgreSQL for production/Docker
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='soleva_db'),
            'USER': config('DB_USER', default='soleva_user'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='postgres'),
            'PORT': config('DB_PORT', default='5432'),
            'OPTIONS': {
                'client_encoding': 'UTF8',
            },
        }
    }

AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Only include static directory if it exists to avoid warnings
STATICFILES_DIRS = []
if (BASE_DIR / 'static').exists():
    STATICFILES_DIRS.append(BASE_DIR / 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework_simplejwt.authentication.JWTAuthentication','rest_framework.authentication.SessionAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend','rest_framework.filters.SearchFilter','rest_framework.filters.OrderingFilter'],
    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.AnonRateThrottle','rest_framework.throttling.UserRateThrottle'],
    'DEFAULT_THROTTLE_RATES': {'anon':'100/hour','user':'1000/hour','login':'5/minute','register':'3/minute','password-reset':'3/hour'},
    'EXCEPTION_HANDLER': 'soleva_backend.utils.custom_exception_handler',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

CORS_ALLOWED_ORIGINS = ['https://solevaeg.com','https://www.solevaeg.com']
CORS_ALLOW_CREDENTIALS = True

REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/1')

CACHES = {'default': {'BACKEND':'django_redis.cache.RedisCache','LOCATION':REDIS_URL,'OPTIONS':{'CLIENT_CLASS':'django_redis.client.DefaultClient'}}}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@solevaeg.com')

FILE_UPLOAD_MAX_MEMORY_SIZE = 10*1024*1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10*1024*1024

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

LOGGING = {
    'version':1,
    'disable_existing_loggers':False,
    'formatters':{'verbose':{'format':'{levelname} {asctime} {module} {process:d} {thread:d} {message}','style':'{'},
                  'simple':{'format':'{levelname} {message}','style':'{'}},
    'handlers':{'file':{'level':'INFO','class':'logging.FileHandler','filename':BASE_DIR/'logs'/'django.log','formatter':'verbose'},
                'console':{'level':'INFO','class':'logging.StreamHandler','formatter':'simple'}},
    'root':{'handlers':['console','file'],'level':'INFO'},
    'loggers':{'django':{'handlers':['console','file'],'level':'INFO','propagate':False}},
}
os.makedirs(BASE_DIR/'logs', exist_ok=True)

PAYMOB_API_KEY = config('PAYMOB_API_KEY', default='')
PAYMOB_SECRET_KEY = config('PAYMOB_SECRET_KEY', default='')
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')

FACEBOOK_PIXEL_ID = config('FACEBOOK_PIXEL_ID', default='')
GOOGLE_ANALYTICS_ID = config('GOOGLE_ANALYTICS_ID', default='')
TIKTOK_PIXEL_ID = config('TIKTOK_PIXEL_ID', default='')
SNAPCHAT_PIXEL_ID = config('SNAPCHAT_PIXEL_ID', default='')
