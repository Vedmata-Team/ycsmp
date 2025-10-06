from django.core.mail import EmailMessage, send_mail
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

def generate_vehicle_pass_for_email(registration):
    """Generate vehicle pass image for email attachment"""
    try:
        from vehicle_pass.views import generate_vehicle_pass
        from django.test import RequestFactory
        from urllib.parse import quote
        
        # Create fake request for vehicle pass generation
        factory = RequestFactory()
        encoded_vehicle = quote(registration.vehicle_number, safe='')
        request = factory.get(f'/vehicle-pass/generate/{registration.id}/{encoded_vehicle}/')
        
        # Generate vehicle pass
        response = generate_vehicle_pass(request, registration.id, registration.vehicle_number)
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"Vehicle pass generation failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error generating vehicle pass for email: {e}")
        return None

def send_registration_approval_email(registration, sent_by_user=None, skip_attachments=False):
    """Send approval email with attachments in single email"""
    
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
        return False
    
    print(f"\n=== COMBINED EMAIL SENDING ===")
    print(f"Email: {registration.email}")
    print(f"Status: {registration.approval_status}")
    has_valid_vehicle = (registration.vehicle_number and 
                         registration.vehicle_number.strip() and 
                         registration.vehicle_number != '-' and 
                         registration.transport_mode == 'car')
    print(f"Has vehicle: {has_valid_vehicle}")
    print(f"Vehicle number: '{registration.vehicle_number}', Transport: {registration.transport_mode}")
    
    context = {
        'registration': registration,
        'event': registration.event,
        'profile_url': registration.get_profile_url(),
        'rejection_reason': getattr(registration, 'rejection_reason', ''),
    }
    
    html_message = render_to_string(template, context)
    success = False
    error_message = ''
    
    try:
        # Create email with HTML content
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[registration.email],
        )
        email.content_subtype = 'html'
        
        # Generate and attach documents for approved users
        if registration.approval_status == 'approved' and not skip_attachments:
            print(f"🔄 Generating attachments for {registration.email}...")
            
            try:
                # Always generate ID card
                id_card_data = generate_id_card_for_email(registration)
                if id_card_data:
                    email.attach(
                        f"id_card_{registration.registration_number or registration.id}.png",
                        id_card_data,
                        'image/png'
                    )
                    print(f"✅ ID card attached")
                else:
                    print(f"⚠️ ID card generation failed")
            except Exception as e:
                print(f"⚠️ ID card attachment failed: {e}")
            
            try:
                # Generate vehicle pass only if user has vehicle
                if (registration.vehicle_number and 
                    registration.vehicle_number.strip() and 
                    registration.vehicle_number != '-' and 
                    registration.transport_mode == 'car'):
                    vehicle_pass_data = generate_vehicle_pass_for_email(registration)
                    if vehicle_pass_data:
                        email.attach(
                            f"vehicle_pass_{registration.registration_number or registration.id}.png",
                            vehicle_pass_data,
                            'image/png'
                        )
                        print(f"✅ Vehicle pass attached")
                    else:
                        print(f"⚠️ Vehicle pass generation failed")
                else:
                    print(f"⚠️ Vehicle pass skipped - no valid vehicle info")
            except Exception as e:
                print(f"⚠️ Vehicle pass attachment failed: {e}")
            
            print(f"✅ Proceeding with email (with or without attachments)")
        
        # Send single email with all content and attachments (with fallback)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                from django.core.mail import get_connection
                connection = get_connection()
                connection.timeout = 15
                email.connection = connection
                
                email.send(fail_silently=False)
                print(f"✅ Combined email sent to {registration.email}")
                success = True
                break
            except Exception as retry_error:
                print(f"⚠️ Email attempt {attempt + 1} failed: {retry_error}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(3)
                    continue
                else:
                    # Try Gmail SMTP as fallback
                    try:
                        print(f"🔄 Trying Gmail SMTP fallback...")
                        from django.core.mail.backends.smtp import EmailBackend
                        gmail_backend = EmailBackend(
                            host='smtp.gmail.com',
                            port=587,
                            username='youthcell@awgp.org',
                            password='PpgPvm@24',
                            use_tls=True,
                            timeout=10
                        )
                        email.connection = gmail_backend
                        email.send(fail_silently=False)
                        print(f"✅ Combined email sent via Gmail fallback to {registration.email}")
                        success = True
                        break
                    except Exception as fallback_error:
                        print(f"❌ Gmail fallback also failed: {fallback_error}")
                        # Last resort: send without attachments
                        try:
                            print(f"🔄 Last resort: sending without attachments...")
                            simple_email = EmailMessage(
                                subject=subject,
                                body=html_message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                to=[registration.email],
                            )
                            simple_email.content_subtype = 'html'
                            simple_email.send(fail_silently=False)
                            print(f"✅ Email sent without attachments to {registration.email}")
                            success = True
                            break
                        except Exception as final_error:
                            print(f"❌ Final attempt failed: {final_error}")
                            raise retry_error
        
    except Exception as e:
        error_message = str(e)
        print(f"❌ Email sending failed: {e}")
        success = False
    
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