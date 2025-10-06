#!/usr/bin/env python3
"""
Test Email Sending with Attachments
"""

import os
import sys
import django

# Setup Django
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration
from events.email_utils import send_registration_approval_email

def test_email_with_attachments():
    print("🔍 TESTING EMAIL WITH ATTACHMENTS")
    print("=" * 50)
    
    try:
        # Get registration 4307 from logs
        registration = EventRegistration.objects.get(id=4307)
        print(f"📋 Registration: {registration.full_name} ({registration.email})")
        print(f"📧 Status: {registration.approval_status}")
        print(f"🚗 Vehicle: '{registration.vehicle_number}' | Transport: {registration.transport_mode}")
        print()
        
        # Test email sending
        print("📧 Sending email with attachments...")
        result = send_registration_approval_email(registration)
        
        if result:
            print("✅ Email sent successfully!")
        else:
            print("❌ Email sending failed!")
            
    except EventRegistration.DoesNotExist:
        print("❌ Registration 4307 not found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_email_with_attachments()