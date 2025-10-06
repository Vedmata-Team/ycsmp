from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.http import HttpResponse
import io
import tempfile
import os

def generate_id_card_for_email(registration):
    """Generate ID card image for email attachment"""
    try:
        from ID.fallback_views import generate_id_card_with_fallback
        from django.test import RequestFactory
        
        # Create fake request for ID card generation
        factory = RequestFactory()
        request = factory.get(f'/id/card/{registration.id}/')
        
        # Generate ID card
        response = generate_id_card_with_fallback(request, registration.id)
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"ID card generation failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error generating ID card for email: {e}")
        return None

def send_registration_approval_email(registration, sent_by_user=None):
    """Send email when registration is approved or rejected"""
    if registration.registration_type == 'volunteer':
        reg_type = 'समयदानी कार्यकर्ता'
    elif registration.registration_type == 'organization_representative':
        reg_type = 'संगठन प्रतिनिधि'
    else:
        reg_type = 'प्रतिभागी'
    
    # Different subject and template based on status
    if registration.approval_status == 'approved':
        subject = f'{reg_type} पंजीकरण अप्रूव - {registration.event.title}'
        template = 'events/emails/registration_approved.html'
        email_type = 'approval'
    elif registration.approval_status == 'rejected':
        subject = f'{reg_type} पंजीकरण अस्वीकृत - {registration.event.title}'
        template = 'events/emails/registration_rejected.html'
        email_type = 'rejection'
    else:
        return False  # Only send for approved/rejected
    
    print(f"\n=== EMAIL SENDING DEBUG ===")
    print(f"Attempting to send email to: {registration.email}")
    print(f"Subject: {subject}")
    print(f"Status: {registration.approval_status}")
    
    context = {
        'registration': registration,
        'event': registration.event,
        'profile_url': registration.get_profile_url(),
        'rejection_reason': getattr(registration, 'rejection_reason', ''),
    }
    
    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)
    
    success = False
    error_message = ''
    
    # Retry logic for email sending
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Create email message
            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[registration.email],
            )
            email.content_subtype = 'html'
            
            # Generate and attach ID card only if approved
            if registration.approval_status == 'approved':
                print("Generating ID card for email attachment...")
                id_card_data = generate_id_card_for_email(registration)
                
                if id_card_data:
                    filename = f"id_card_{registration.registration_number or registration.id}.png"
                    email.attach(filename, id_card_data, 'image/png')
                    print(f"ID card attached to email: {filename}")
                else:
                    print("Failed to generate ID card for attachment")
            
            email.send(fail_silently=False)
            print(f"Email sent successfully to {registration.email}")
            success = True
            break  # Success, exit retry loop
            
        except Exception as e:
            error_message = str(e)
            print(f"Email sending attempt {attempt + 1} failed: {e}")
            
            if attempt == max_retries - 1:  # Last attempt
                import traceback
                print(f"All email attempts failed. Full traceback: {traceback.format_exc()}")
            else:
                print(f"Retrying in 2 seconds... ({attempt + 1}/{max_retries})")
                import time
                time.sleep(2)

    
    # Log email attempt
    try:
        from .models import EmailLog
        EmailLog.objects.create(
            registration=registration,
            email_type=email_type,
            sent_by=sent_by_user,
            success=success,
            error_message=error_message
        )
    except Exception as log_error:
        print(f"Failed to log email: {log_error}")
    
    return success

def send_registration_details_email(registration):
    """Send registration details email (for resend functionality)"""
    if registration.registration_type == 'volunteer':
        reg_type = 'समयदानी कार्यकर्ता'
    elif registration.registration_type == 'organization_representative':
        reg_type = 'संगठन प्रतिनिधि'
    else:
        reg_type = 'प्रतिभागी'
    
    subject = f'{reg_type} पंजीकरण विवरण - {registration.event.title}'
    
    print(f"\n=== EMAIL RESEND DEBUG ===")
    print(f"Attempting to resend email to: {registration.email}")
    print(f"Subject: {subject}")
    
    context = {
        'registration': registration,
        'event': registration.event,
        'profile_url': registration.get_profile_url(),
    }
    
    html_message = render_to_string('events/emails/registration_details.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"Email resent successfully to {registration.email}")
        return True
    except Exception as e:
        print(f"Email resending failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False