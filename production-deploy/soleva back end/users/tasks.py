from celery import shared_task
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def cleanup_expired_sessions():
    """
    Clean up expired Django sessions from the database
    """
    try:
        # Get sessions older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)

        # Delete expired sessions
        expired_sessions = Session.objects.filter(expire_date__lt=cutoff_date)
        deleted_count = expired_sessions.count()
        expired_sessions.delete()

        logger.info(f"Cleaned up {deleted_count} expired sessions")
        return deleted_count

    except Exception as e:
        logger.error(f"Error in cleanup_expired_sessions task: {str(e)}")
        return 0
