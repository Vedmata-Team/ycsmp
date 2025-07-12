from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

def send_registration_approval_email(registration):
    """Send email when registration is fully approved"""
    subject = f'पंजीकरण अप्रूव - {registration.event.title}'
    
    context = {
        'registration': registration,
        'event': registration.event,
    }
    
    html_message = render_to_string('events/emails/registration_approved.html', context)
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
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def send_registration_details_email(registration):
    """Send registration details email (for resend functionality)"""
    subject = f'पंजीकरण विवरण - {registration.event.title}'
    
    context = {
        'registration': registration,
        'event': registration.event,
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
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False