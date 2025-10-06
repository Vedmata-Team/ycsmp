#!/usr/bin/env python3
"""
Test Registration 4308
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

def test_registration():
    print("🔍 TESTING FULL EMAIL FLOW")
    print("=" * 50)
    
    try:
        registration = EventRegistration.objects.get(id=4308)
        print(f"📋 Registration: {registration.full_name}")
        print(f"📧 Email: {registration.email}")
        print(f"📊 Status: {registration.approval_status}")
        print(f"🔢 Reg Number: {registration.registration_number}")
        print(f"✅ Confirmed: {registration.is_confirmed}")
        print(f"📧 Email Sent: {registration.email_sent}")
        
        # Test full email flow with attachments
        print(f"\n🧪 Testing complete email flow with attachments...")
        from events.email_utils import send_registration_approval_email
        
        result = send_registration_approval_email(registration)
        
        if result:
            print(f"✅ Full email flow successful!")
            # Update email sent status
            registration.email_sent = True
            registration.save(update_fields=['email_sent'])
        else:
            print(f"❌ Full email flow failed!")
        
    except EventRegistration.DoesNotExist:
        print("❌ Registration 4308 not found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_registration()