"""
Ultra-fast email system - optimized for speed and reliability
Replaces the existing slow email_utils.py system
"""

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import logging
import time
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)

class FastEmailSender:
    """Ultra-fast email sender with optimized connection handling"""
    
    def __init__(self):
        self.connection_lock = threading.Lock()
        
    def send_email_fast(self, to_email, subject, html_content, attachments=None):
        """Send email with minimal overhead"""
        start_time = time.time()
        
        try:
            from django.core.mail import send_mail
            from django.utils.html import strip_tags
            
            # For simple emails without attachments - use send_mail (fastest)
            if not attachments:
                plain_message = strip_tags(html_content)
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[to_email],
                    html_message=html_content,
                    fail_silently=False,
                )
            else:
                # For emails with attachments - use EmailMessage
                email = EmailMessage(
                    subject=subject,
                    body=html_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[to_email],
                )
                email.content_subtype = 'html'
                
                # Add attachments
                for filename, data, content_type in attachments:
                    if data and len(data) > 0:
                        email.attach(filename, data, content_type)
                
                email.send(fail_silently=False)
            
            elapsed = time.time() - start_time
            logger.info(f"Email sent to {to_email} in {elapsed:.2f}s")
            return True
                
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Email failed to {to_email} after {elapsed:.2f}s: {e}")
            return False

# Global email sender instance
email_sender = FastEmailSender()

def generate_documents_async(registration):
    """Generate documents in background thread - non-blocking"""
    def _generate():
        documents = {}
        
        try:
            # Generate ID card
            from ID.fallback_views import generate_id_card_with_fallback
            from django.test import RequestFactory
            
            factory = RequestFactory()
            request = factory.get(f'/id/card/{registration.id}/')
            response = generate_id_card_with_fallback(request, registration.id)
            
            if response.status_code == 200:
                documents['id_card'] = response.content
                
        except Exception as e:
            logger.error(f"ID card generation failed: {e}")
        
        try:
            # Generate vehicle pass if needed
            if (registration.vehicle_number and 
                registration.vehicle_number.strip() and 
                registration.vehicle_number != '-' and 
                registration.transport_mode == 'car'):
                
                from vehicle_pass.views import generate_vehicle_pass
                from urllib.parse import quote
                
                factory = RequestFactory()
                encoded_vehicle = quote(registration.vehicle_number, safe='')
                request = factory.get(f'/vehicle-pass/generate/{registration.id}/{encoded_vehicle}/')
                response = generate_vehicle_pass(request, registration.id, registration.vehicle_number)
                
                if response.status_code == 200:
                    documents['vehicle_pass'] = response.content
                    
        except Exception as e:
            logger.error(f"Vehicle pass generation failed: {e}")
        
        return documents
    
    # Run in thread pool
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_generate)
        return future

def send_approval_email_ultra_fast(registration):
    """Ultra-fast email sending - main function"""
    start_time = time.time()
    
    try:
        # Determine email type and subject
        if registration.registration_type == 'volunteer':
            reg_type = 'समयदानी कार्यकर्ता'
        elif registration.registration_type == 'organization_representative':
            reg_type = 'संगठन प्रतिनिधि'
        else:
            reg_type = 'प्रतिभागी'
        
        if registration.approval_status == 'approved':
            subject = f'{reg_type} पंजीकरण अप्रूव - {registration.event.title}'
            template = 'events/emails/registration_approved.html'
        elif registration.approval_status == 'rejected':
            subject = f'{reg_type} पंजीकरण अस्वीकृत - {registration.event.title}'
            template = 'events/emails/registration_rejected.html'
        else:
            return False
        
        # Generate HTML content (fast)
        context = {
            'registration': registration,
            'event': registration.event,
            'profile_url': registration.get_profile_url(),
            'rejection_reason': getattr(registration, 'rejection_reason', ''),
        }
        html_content = render_to_string(template, context)
        
        # For approved registrations, generate documents in background
        attachments = []
        if registration.approval_status == 'approved':
            # Start document generation in background
            doc_future = generate_documents_async(registration)
            
            # Wait maximum 2 seconds for documents
            try:
                documents = doc_future.result(timeout=2.0)
                
                if 'id_card' in documents:
                    attachments.append((
                        f"id_card_{registration.registration_number or registration.id}.png",
                        documents['id_card'],
                        'image/png'
                    ))
                
                if 'vehicle_pass' in documents:
                    attachments.append((
                        f"vehicle_pass_{registration.registration_number or registration.id}.png",
                        documents['vehicle_pass'],
                        'image/png'
                    ))
                    
            except Exception as e:
                logger.warning(f"Document generation timeout or failed: {e}")
                # Continue without attachments
        
        # Send email with fast sender
        success = email_sender.send_email_fast(
            registration.email,
            subject,
            html_content,
            attachments
        )
        
        # Log result
        elapsed = time.time() - start_time
        logger.info(f"Total email process completed in {elapsed:.2f}s - Success: {success}")
        
        # Log to database and update email_sent flag
        try:
            from .models import EmailLog
            EmailLog.objects.create(
                registration=registration,
                email_type='approval' if registration.approval_status == 'approved' else 'rejection',
                sent_by=None,
                success=success,
                error_message='' if success else 'Fast email system failure'
            )
            
            # Update email_sent flag if email was successful
            if success:
                from .models import EventRegistration
                EventRegistration.objects.filter(pk=registration.pk).update(email_sent=True)
                logger.info(f"Email_sent flag updated for registration {registration.pk}")
                
        except Exception as log_error:
            logger.error(f"Failed to log email or update flag: {log_error}")
        
        return success
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Ultra-fast email failed after {elapsed:.2f}s: {e}")
        return False

def send_simple_email_fast(registration):
    """Send email without any attachments - ultra fast"""
    start_time = time.time()
    
    try:
        # Determine subject
        if registration.registration_type == 'volunteer':
            reg_type = 'समयदानी कार्यकर्ता'
        elif registration.registration_type == 'organization_representative':
            reg_type = 'संगठन प्रतिनिधि'
        else:
            reg_type = 'प्रतिभागी'
        
        subject = f'{reg_type} पंजीकरण अप्रूव - {registration.event.title}'
        
        # Generate HTML content
        context = {
            'registration': registration,
            'event': registration.event,
            'profile_url': registration.get_profile_url(),
        }
        html_content = render_to_string('events/emails/registration_approved.html', context)
        
        # Send email without attachments
        success = email_sender.send_email_fast(
            registration.email,
            subject,
            html_content,
            None  # No attachments
        )
        
        elapsed = time.time() - start_time
        logger.info(f"Simple email completed in {elapsed:.2f}s - Success: {success}")
        
        # Update email_sent flag if successful
        if success:
            try:
                from .models import EventRegistration
                EventRegistration.objects.filter(pk=registration.pk).update(email_sent=True)
                logger.info(f"Simple email flag updated for registration {registration.pk}")
            except Exception as flag_error:
                logger.error(f"Failed to update email_sent flag: {flag_error}")
        
        return success
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Simple email failed after {elapsed:.2f}s: {e}")
        return False