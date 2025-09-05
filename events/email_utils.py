from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

def send_registration_approval_email(registration):
    """Send email when registration is fully approved"""
    reg_type = 'समयदानी कार्यकर्ता' if registration.registration_type == 'volunteer' else 'प्रतिभागी'
    subject = f'{reg_type} पंजीकरण अप्रूव - {registration.event.title}'
    
    print(f"\n=== EMAIL SENDING DEBUG ===")
    print(f"Attempting to send email to: {registration.email}")
    print(f"Subject: {subject}")
    print(f"From email: {settings.DEFAULT_FROM_EMAIL}")
    print(f"SMTP Host: {settings.EMAIL_HOST}")
    print(f"SMTP Port: {settings.EMAIL_PORT}")
    print(f"Use TLS: {settings.EMAIL_USE_TLS}")
    
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
        print(f"Email sent successfully to {registration.email}")
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

def send_registration_details_email(registration):
    """Send registration details email (for resend functionality)"""
    reg_type = 'सहयोगी कार्यकर्ता' if registration.registration_type == 'volunteer' else 'प्रतिभागी'
    subject = f'{reg_type} पंजीकरण विवरण - {registration.event.title}'
    
    print(f"\n=== EMAIL RESEND DEBUG ===")
    print(f"Attempting to resend email to: {registration.email}")
    print(f"Subject: {subject}")
    
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
        print(f"Email resent successfully to {registration.email}")
        return True
    except Exception as e:
        print(f"Email resending failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False