import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soleva_backend.settings')

app = Celery('soleva_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'send-pending-emails': {
        'task': 'notifications.tasks.send_pending_emails',
        'schedule': 60.0,  # Run every minute
    },
    'send-pending-sms': {
        'task': 'notifications.tasks.send_pending_sms',
        'schedule': 60.0,  # Run every minute
    },
    'cleanup-expired-sessions': {
        'task': 'users.tasks.cleanup_expired_sessions',
        'schedule': 3600.0,  # Run every hour
    },
    'process-abandoned-carts': {
        'task': 'cart.tasks.process_abandoned_carts',
        'schedule': 1800.0,  # Run every 30 minutes
    },
    'update-inventory-alerts': {
        'task': 'products.tasks.check_low_stock',
        'schedule': 3600.0,  # Run every hour
    },
}

app.conf.timezone = 'Africa/Cairo'


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
