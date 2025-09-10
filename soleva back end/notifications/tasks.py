from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_pending_emails():
    """
    Send pending email notifications
    """
    try:
        pending_emails = Notification.objects.filter(
            type='email',
            status='pending'
        ).select_related('user')[:50]  # Process in batches

        sent_count = 0
        for notification in pending_emails:
            try:
                send_mail(
                    subject=notification.title,
                    message=notification.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[notification.user.email],
                    fail_silently=False,
                )
                notification.status = 'sent'
                notification.save()
                sent_count += 1
                logger.info(f"Email sent to {notification.user.email}")
            except Exception as e:
                notification.status = 'failed'
                notification.save()
                logger.error(f"Failed to send email to {notification.user.email}: {str(e)}")

        logger.info(f"Processed {sent_count} pending emails")
        return sent_count

    except Exception as e:
        logger.error(f"Error in send_pending_emails task: {str(e)}")
        return 0


@shared_task
def send_pending_sms():
    """
    Send pending SMS notifications
    Note: This requires SMS gateway integration
    """
    try:
        pending_sms = Notification.objects.filter(
            type='sms',
            status='pending'
        ).select_related('user')[:50]  # Process in batches

        sent_count = 0
        for notification in pending_sms:
            try:
                # TODO: Implement SMS sending logic here
                # This would typically integrate with services like:
                # - Twilio, AWS SNS, Firebase Cloud Messaging, etc.

                logger.info(f"SMS would be sent to {notification.user.phone}: {notification.message}")
                notification.status = 'sent'
                notification.save()
                sent_count += 1

            except Exception as e:
                notification.status = 'failed'
                notification.save()
                logger.error(f"Failed to send SMS to {notification.user.phone}: {str(e)}")

        logger.info(f"Processed {sent_count} pending SMS messages")
        return sent_count

    except Exception as e:
        logger.error(f"Error in send_pending_sms task: {str(e)}")
        return 0
