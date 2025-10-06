# Import the new fast email system
from .fast_email_system import send_approval_email_ultra_fast, send_simple_email_fast
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

def send_registration_approval_email(registration, sent_by_user=None, skip_attachments=False):
    """Ultra-fast email sending - replaces old slow system"""
    print(f"\n=== ULTRA-FAST EMAIL SYSTEM ===")
    print(f"Email: {registration.email}")
    print(f"Status: {registration.approval_status}")
    print(f"Skip attachments: {skip_attachments}")
    
    try:
        if skip_attachments:
            # Send simple email without attachments (fastest)
            success = send_simple_email_fast(registration)
            print(f"✅ Simple email result: {success}")
        else:
            # Send email with attachments (fast with timeout)
            success = send_approval_email_ultra_fast(registration)
            print(f"✅ Full email result: {success}")
        
        return success
        
    except Exception as e:
        logger.error(f"Ultra-fast email system failed: {e}")
        print(f"❌ Ultra-fast email failed: {e}")
        return False

def send_registration_details_email(registration):
    """Send registration details email (for resend functionality) - FAST VERSION"""
    print(f"\n=== FAST EMAIL RESEND ===")
    print(f"Resending to: {registration.email}")
    
    try:
        # Use the ultra-fast system for resends too
        success = send_simple_email_fast(registration)
        print(f"Fast resend result: {success}")
        return success
    except Exception as e:
        logger.error(f"Fast email resend failed: {e}")
        print(f"❌ Fast resend failed: {e}")
        return False