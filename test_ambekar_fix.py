#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')

# Setup Django
django.setup()

from django.contrib.auth.models import User
from events.models import ApprovalUser, EventRegistration
from events.admin import EventRegistrationAdmin
from django.test import RequestFactory

def test_ambekar_approval_buttons():
    print("🧪 Testing Ambekar_mp approval button fix...")
    
    # Get Ambekar user
    user = User.objects.filter(username__icontains='ambekar').first()
    if not user:
        print("❌ Ambekar user not found!")
        return
    
    print(f"✅ Found user: {user.username}")
    
    # Get approval user
    try:
        approval_user = ApprovalUser.objects.get(user=user)
        print(f"✅ ApprovalUser found - Super Approver: {approval_user.is_super_approver}")
    except ApprovalUser.DoesNotExist:
        print("❌ ApprovalUser not found!")
        return
    
    # Get a test registration
    test_registration = EventRegistration.objects.filter(approval_status='pending').first()
    if not test_registration:
        test_registration = EventRegistration.objects.filter(approval_status='district_approved').first()
    if not test_registration:
        test_registration = EventRegistration.objects.filter(approval_status='upzone_approved').first()
    
    if not test_registration:
        print("❌ No test registration found!")
        return
    
    print(f"✅ Testing with registration: {test_registration.full_name} (Status: {test_registration.approval_status})")
    
    # Create mock request
    factory = RequestFactory()
    request = factory.get('/admin/')
    request.user = user
    
    # Test admin approval buttons
    admin = EventRegistrationAdmin(EventRegistration, None)
    buttons = admin.get_approval_buttons(request, test_registration)
    
    print(f"\n🔘 Available approval buttons for {test_registration.approval_status} registration:")
    if buttons:
        for button in buttons:
            print(f"   ✅ {button['label']} ({button['name']})")
    else:
        print("   ❌ No buttons available!")
    
    # Test expected buttons based on status
    expected_buttons = []
    if test_registration.approval_status == 'pending':
        expected_buttons = ['_approve_district']
    elif test_registration.approval_status == 'district_approved':
        expected_buttons = ['_approve_upzone']
    elif test_registration.approval_status == 'upzone_approved':
        expected_buttons = ['_approve_final']
    
    actual_button_names = [b['name'] for b in buttons if b['name'] != '_reject']
    
    print(f"\n📊 Test Results:")
    print(f"   Expected: {expected_buttons}")
    print(f"   Actual: {actual_button_names}")
    
    if set(expected_buttons).issubset(set(actual_button_names)):
        print("   ✅ SUCCESS: All expected buttons are available!")
    else:
        print("   ❌ FAILED: Missing expected buttons!")
    
    # Test rejection button
    if any(b['name'] == '_reject' for b in buttons):
        print("   ✅ Reject button available")
    else:
        print("   ❌ Reject button missing")

if __name__ == "__main__":
    test_ambekar_approval_buttons()