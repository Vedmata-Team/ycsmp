#!/usr/bin/env python
"""
Simple email test script to verify SMTP configuration
Run this script to test email sending without Django overhead
"""

import os
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_smtp_connection():
    """Test SMTP connection and email sending"""
    print("=== EMAIL CONFIGURATION TEST ===")
    print(f"SMTP Host: {settings.EMAIL_HOST}")
    print(f"SMTP Port: {settings.EMAIL_PORT}")
    print(f"Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"From email: {settings.DEFAULT_FROM_EMAIL}")
    print(f"Host user: {settings.EMAIL_HOST_USER}")
    print(f"Host password: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'Not set'}")
    
    # Test basic SMTP connection
    try:
        import smtplib
        print("\n=== TESTING SMTP CONNECTION ===")
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        print("✓ SMTP connection successful")
        server.quit()
    except Exception as e:
        print(f"✗ SMTP connection failed: {e}")
        return False
    
    # Test Django email sending
    try:
        print("\n=== TESTING DJANGO EMAIL SENDING ===")
        send_mail(
            subject='Test Email - YCS MP Registration System',
            message='This is a test email to verify the email configuration is working properly.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['youthcell@awgp.org'],  # Using the same email as sender for testing
            fail_silently=False,
        )
        print("✓ Django email sending successful")
        return True
    except Exception as e:
        print(f"✗ Django email sending failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_smtp_connection()