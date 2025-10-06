#!/usr/bin/env python
import os
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')

import django
django.setup()

from django.contrib.auth.models import User
from events.models import EventRegistration
from events.email_utils import send_registration_approval_email

def test_divya_complete_process():
    print("🧪 Testing Complete Process for Divya Mohan Singh...")
    
    # Find registration
    registration = EventRegistration.objects.filter(
        email="vedmatawebdesigning@gmail.com"
    ).first()
    
    if not registration:
        print("❌ Registration not found")
        return
    
    print(f"✅ Found: {registration.full_name}")
    print(f"   Status: {registration.approval_status}")
    print(f"   Vehicle: {registration.vehicle_number}")
    print(f"   Transport: {registration.transport_mode}")
    
    # Reset to pending for full test
    if registration.approval_status != 'pending':
        print("\n🔄 Resetting to pending status for full test...")
        registration.approval_status = 'pending'
        registration.registration_number = None
        registration.email_sent = False
        registration.district_approver = None
        registration.upzone_approver = None
        registration.final_approver = None
        registration.save()
        print("   ✅ Reset complete")
    
    # Get Ambekar user
    ambekar = User.objects.filter(username__icontains='ambekar').first()
    if not ambekar:
        print("❌ Ambekar user not found")
        return
    
    print(f"\n👤 Using approver: {ambekar.username}")
    
    # Step 1: District Approval
    print("\n📍 Step 1: District Approval")
    registration.approval_status = 'district_approved'
    registration.district_approver = ambekar
    registration.save()
    print(f"   ✅ Status: {registration.approval_status}")
    
    # Step 2: UpZone Approval
    print("\n🏢 Step 2: UpZone Approval")
    registration.approval_status = 'upzone_approved'
    registration.upzone_approver = ambekar
    registration.save()
    print(f"   ✅ Status: {registration.approval_status}")
    
    # Step 3: Final Approval with Email
    print("\n🎯 Step 3: Final Approval with Email & Attachments")
    registration.approval_status = 'approved'
    registration.final_approver = ambekar
    registration.save()  # This should trigger email with ID card and vehicle pass
    
    print(f"   ✅ Status: {registration.approval_status}")
    print(f"   ✅ Registration Number: {registration.registration_number}")
    print(f"   ✅ Email Sent Flag: {registration.email_sent}")
    
    # Test manual email sending
    print("\n📧 Testing Manual Email with Attachments...")
    email_success = send_registration_approval_email(registration, ambekar)
    print(f"   Email Success: {email_success}")
    
    # Check what attachments should be included
    print(f"\n📎 Expected Email Attachments:")
    print(f"   1. ID Card: id_card_{registration.registration_number}.png")
    if registration.vehicle_number and registration.transport_mode == 'car':
        print(f"   2. Vehicle Pass: vehicle_pass_{registration.registration_number}.png")
        print(f"      Vehicle Number: {registration.vehicle_number}")
    else:
        print(f"   2. No vehicle pass (no vehicle or not car)")
    
    # Test URLs
    print(f"\n🔗 Test URLs:")
    print(f"   ID Card: /id/card/{registration.id}/")
    if registration.vehicle_number:
        from urllib.parse import quote
        print(f"   Vehicle Pass: /vehicle-pass/generate/{registration.id}/{quote(registration.vehicle_number, safe='')}/")
    
    print(f"\n✅ Complete test finished for {registration.full_name}")
    print(f"📧 Check email: {registration.email}")

if __name__ == "__main__":
    test_divya_complete_process()