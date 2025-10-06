#!/usr/bin/env python
import os
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')

import django
django.setup()

from django.contrib.auth.models import User
from events.models import EventRegistration, ApprovalUser
from events.admin import EventRegistrationAdmin
from django.test import RequestFactory

def test_divya_approval():
    print("🧪 Testing Divya Mohan Singh approval workflow...")
    
    # Find the registration
    registration = EventRegistration.objects.filter(
        full_name__icontains="Divya Mohan Singh",
        email="vedmatawebdesigning@gmail.com",
        phone="09506933715"
    ).first()
    
    # Also try searching by partial name if not found
    if not registration:
        registration = EventRegistration.objects.filter(
            full_name__icontains="Divya",
            email="vedmatawebdesigning@gmail.com"
        ).first()
    
    # Try searching by email only
    if not registration:
        registration = EventRegistration.objects.filter(
            email="vedmatawebdesigning@gmail.com"
        ).first()
    
    if not registration:
        print("❌ Registration not found for Divya Mohan Singh")
        return
    
    print(f"✅ Found registration: {registration.full_name}")
    print(f"   Email: {registration.email}")
    print(f"   Phone: {registration.phone}")
    print(f"   City: {registration.city}")
    print(f"   State: {registration.state}")
    print(f"   Type: {registration.registration_type}")
    print(f"   Current Status: {registration.approval_status}")
    print(f"   Registration Number: {registration.registration_number or 'Not generated'}")
    
    # Test with Ambekar_mp (Super Approver)
    ambekar_user = User.objects.filter(username__icontains='ambekar').first()
    if not ambekar_user:
        print("❌ Ambekar_mp user not found")
        return
    
    print(f"\n🔍 Testing with Super Approver: {ambekar_user.username}")
    
    # Create mock request
    factory = RequestFactory()
    request = factory.get('/admin/')
    request.user = ambekar_user
    
    # Test admin approval buttons
    admin = EventRegistrationAdmin(EventRegistration, None)
    buttons = admin.get_approval_buttons(request, registration)
    
    print(f"\n🔘 Available approval buttons for {registration.approval_status} registration:")
    if buttons:
        for button in buttons:
            print(f"   ✅ {button['label']} ({button['name']})")
    else:
        print("   ❌ No buttons available!")
    
    # Test approval workflow
    print(f"\n🔄 Testing approval workflow...")
    
    if registration.approval_status == 'pending':
        print("   Step 1: District Approval")
        registration.approval_status = 'district_approved'
        registration.district_approver = ambekar_user
        registration.save()
        print(f"   ✅ Status: {registration.approval_status}")
        
        print("   Step 2: UpZone Approval")
        registration.approval_status = 'upzone_approved'
        registration.upzone_approver = ambekar_user
        registration.save()
        print(f"   ✅ Status: {registration.approval_status}")
        
        print("   Step 3: Final Approval")
        registration.approval_status = 'approved'
        registration.final_approver = ambekar_user
        registration.save()
        print(f"   ✅ Status: {registration.approval_status}")
        print(f"   ✅ Registration Number: {registration.registration_number}")
        print(f"   ✅ Email Sent: {registration.email_sent}")
        
    elif registration.approval_status == 'district_approved':
        print("   Starting from UpZone Approval")
        registration.approval_status = 'upzone_approved'
        registration.upzone_approver = ambekar_user
        registration.save()
        print(f"   ✅ Status: {registration.approval_status}")
        
        print("   Step 3: Final Approval")
        registration.approval_status = 'approved'
        registration.final_approver = ambekar_user
        registration.save()
        print(f"   ✅ Status: {registration.approval_status}")
        print(f"   ✅ Registration Number: {registration.registration_number}")
        
    elif registration.approval_status == 'upzone_approved':
        print("   Starting from Final Approval")
        registration.approval_status = 'approved'
        registration.final_approver = ambekar_user
        registration.save()
        print(f"   ✅ Status: {registration.approval_status}")
        print(f"   ✅ Registration Number: {registration.registration_number}")
        
    elif registration.approval_status == 'approved':
        print("   ✅ Already approved!")
        print(f"   Registration Number: {registration.registration_number}")
        print(f"   Email Sent: {registration.email_sent}")
        
    else:
        print(f"   Status: {registration.approval_status}")
    
    # Test ID card generation URL
    print(f"\n🆔 ID Card URL: /id/card/{registration.id}/")
    
    # Test vehicle pass if available
    if registration.vehicle_number:
        from urllib.parse import quote
        vehicle_url = f"/vehicle-pass/generate/{registration.id}/{quote(registration.vehicle_number, safe='')}"
        print(f"🚗 Vehicle Pass URL: {vehicle_url}")
        print(f"   Vehicle Number: {registration.vehicle_number}")
        print(f"   Transport Mode: {registration.transport_mode}")
    else:
        print("🚗 No vehicle number provided")
    
    # Test JavaScript workflow simulation
    print(f"\n💻 JavaScript Workflow Test:")
    print(f"   1. ID Card URL: /id/card/{registration.id}/")
    if registration.vehicle_number:
        print(f"   2. Vehicle Pass URL: /vehicle-pass/generate/{registration.id}/{quote(registration.vehicle_number, safe='')}/")
        print(f"   3. Final approval will generate BOTH ID card and vehicle pass")
    else:
        print(f"   2. No vehicle pass needed")
        print(f"   3. Final approval will generate ID card only")
    
    print(f"\n✅ Test completed for {registration.full_name}")
    print(f"\n💼 Admin URL: /control/events/eventregistration/{registration.id}/change/")

if __name__ == "__main__":
    test_divya_approval()