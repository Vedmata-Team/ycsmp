#!/usr/bin/env python3
import os
import sys
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration
from events.email_utils import send_registration_approval_email

def test_email_speed():
    print("🧪 Testing Fast Email System")
    
    # Find test registration
    reg = EventRegistration.objects.filter(
        approval_status='approved',
        email__isnull=False
    ).exclude(email='').first()
    
    if not reg:
        print("❌ No test registration found")
        return False
    
    print(f"Testing with: {reg.full_name} ({reg.email})")
    
    # Test simple email
    print("\n⚡ Testing simple email...")
    start = time.time()
    success = send_registration_approval_email(reg, skip_attachments=True)
    elapsed = time.time() - start
    
    print(f"Result: {'✅' if success else '❌'} {elapsed:.2f}s")
    
    # Test full email
    print("\n📎 Testing email with attachments...")
    start = time.time()
    success = send_registration_approval_email(reg)
    elapsed = time.time() - start
    
    print(f"Result: {'✅' if success else '❌'} {elapsed:.2f}s")
    
    return success

if __name__ == "__main__":
    test_email_speed()