from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.cache import cache
from .models import EventRegistration
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_registration_email_async(self, registration_id, email_type='confirmation'):
    """
    Async task to send registration emails
    """
    try:
        registration = EventRegistration.objects.select_related('event').get(id=registration_id)
        
        if email_type == 'confirmation':
            subject = f'पंजीकरण पुष्टि - {registration.event.title if registration.event else "युवा चिंतन शिविर"}'
            template = 'events/emails/registration_confirmation.html'
        elif email_type == 'approval':
            subject = f'पंजीकरण स्वीकृत - {registration.event.title if registration.event else "युवा चिंतन शिविर"}'
            template = 'events/emails/registration_approved.html'
        else:
            return False
            
        html_message = render_to_string(template, {
            'registration': registration,
            'event': registration.event,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Email sent successfully to {registration.email} for registration {registration_id}")
        return True
        
    except EventRegistration.DoesNotExist:
        logger.error(f"Registration {registration_id} not found")
        return False
    except Exception as exc:
        logger.error(f"Email sending failed for registration {registration_id}: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@shared_task
def send_bulk_emails_async(registration_ids, email_type='confirmation'):
    """
    Send bulk emails for multiple registrations
    """
    success_count = 0
    for reg_id in registration_ids:
        try:
            send_registration_email_async.delay(reg_id, email_type)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to queue email for registration {reg_id}: {str(e)}")
    
    return f"Queued {success_count} emails out of {len(registration_ids)}"

@shared_task
def cleanup_cache_task():
    """
    Periodic task to cleanup expired cache entries
    """
    try:
        # Clear specific cache patterns
        cache.delete_many([
            'event_stats',
            'featured_events',
            'total_registrations',
            'pending_approvals'
        ])
        logger.info("Cache cleanup completed")
        return True
    except Exception as e:
        logger.error(f"Cache cleanup failed: {str(e)}")
        return False

@shared_task
def generate_registration_reports_async():
    """
    Generate registration reports asynchronously
    """
    try:
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        # Generate daily stats
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        daily_stats = EventRegistration.objects.filter(
            created_at__date=yesterday
        ).aggregate(
            total=Count('id'),
            approved=Count('id', filter=Q(approval_status='approved')),
            pending=Count('id', filter=Q(approval_status='pending'))
        )
        
        # Cache the stats
        cache.set(f'daily_stats_{yesterday}', daily_stats, timeout=86400)  # 24 hours
        
        logger.info(f"Daily report generated for {yesterday}: {daily_stats}")
        return daily_stats
        
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        return False