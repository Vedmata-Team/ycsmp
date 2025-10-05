#!/usr/bin/env python
"""
Test rejection email preview
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration, Event
from events.email_utils import send_registration_approval_email
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def send_rejection_preview():
    """Send rejection email preview"""
    
    # Get any registration for testing
    registration = EventRegistration.objects.first()
    if not registration:
        print("No registrations found!")
        return
    
    # Create test data
    class TestRegistration:
        full_name = 'दिव्य मोहन'
        phone = '9999999999'
        email = 'divymohan.awgp@gmail.com'
        registration_type = 'participant'
        state = 'Madhya Pradesh'
        city = 'Bhopal'
        approval_status = 'rejected'
        rejection_reason = 'दस्तावेज़ स्पष्ट नहीं हैं। कृपया स्पष्ट फोटो के साथ पुनः आवेदन करें।'
        
        def get_registration_type_display(self):
            return 'प्रतिभागी'
        
        def get_profile_url(self):
            return '/profile/9999999999_दिव्य_मोहन/'
    
    test_registration = TestRegistration()
    
    class TestEvent:
        title = 'प्रान्तीय युवा चिंतन शिविर भोपाल 2025'
    
    test_event = TestEvent()
    
    # Email details
    subject = 'प्रतिभागी पंजीकरण अस्वीकृत - प्रान्तीय युवा चिंतन शिविर भोपाल 2025'
    
    context = {
        'registration': test_registration,
        'event': test_event,
        'profile_url': test_registration.get_profile_url(),
        'rejection_reason': test_registration.rejection_reason,
    }
    
    html_message = render_to_string('events/emails/registration_rejected.html', context)
    
    try:
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['divymohan.awgp@gmail.com'],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)
        
        print("✅ Rejection email preview sent successfully!")
        print(f"📧 Sent to: divymohan.awgp@gmail.com")
        print(f"📝 Subject: {subject}")
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")

if __name__ == "__main__":
    send_rejection_preview()