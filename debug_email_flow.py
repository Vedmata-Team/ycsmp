#!/usr/bin/env python3
"""
Debug Email Flow - Analyze why combined email logic isn't being used
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycsmp.settings')

try:
    import django
    django.setup()
    from events.models import EventRegistration
    from events.email_utils import send_registration_approval_email
    DJANGO_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Django setup failed: {e}")
    print("Running file analysis only...")
    DJANGO_AVAILABLE = False

def debug_email_flow():
    print("🔍 DEBUGGING EMAIL FLOW")
    print("=" * 50)
    
    if DJANGO_AVAILABLE:
        # Get registration 4306 from logs
        try:
            registration = EventRegistration.objects.get(id=4306)
            print(f"📋 Registration: {registration.name} ({registration.email})")
            print(f"📧 Status: {registration.status}")
            print(f"🚗 Vehicle: '{registration.vehicle_number}' | Transport: {registration.transport_mode}")
            print()
            
            # Check vehicle validation logic
            print("🔍 VEHICLE VALIDATION CHECK:")
            has_valid_vehicle = (
                registration.vehicle_number and 
                registration.vehicle_number.strip() != '' and 
                registration.vehicle_number.strip() != '-' and
                registration.transport_mode == 'car'
            )
            print(f"   Vehicle number: '{registration.vehicle_number}'")
            print(f"   Transport mode: '{registration.transport_mode}'")
            print(f"   Has valid vehicle: {has_valid_vehicle}")
            print()
            
        except EventRegistration.DoesNotExist:
            print("❌ Registration 4306 not found")
        except Exception as e:
            print(f"❌ Database error: {e}")
    else:
        print("⚠️ Skipping database checks - Django not available")
    
    print("\n" + "=" * 50)
    print("🔍 CHECKING EMAIL LOGIC LOCATIONS:")
    
    # Check admin.py for email triggers
    print("\n📁 events/admin.py:")
    try:
        with open('events/admin.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'send_registration_approval_email' in content:
                print("   ✅ Uses combined email function")
                count = content.count('send_registration_approval_email')
                print(f"   📊 Found {count} references to combined email function")
            else:
                print("   ❌ May be using old email logic")
                if 'send_mail(' in content:
                    print("   ⚠️ Found direct send_mail() calls")
    except Exception as e:
        print(f"   ❌ Could not read admin.py: {e}")
    
    # Check models.py for auto email
    print("\n📁 events/models.py:")
    try:
        with open('events/models.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'Auto email disabled' in content:
                print("   ✅ Auto email is disabled")
            elif 'send_email' in content and 'save(' in content:
                print("   ⚠️ Auto email may still be active")
            else:
                print("   ✅ No auto email found")
                
            if 'def save(' in content and ('send_mail' in content or 'email' in content):
                print("   🔍 Found email-related code in save() method")
    except Exception as e:
        print(f"   ❌ Could not read models.py: {e}")
    
    # Check views.py for resend logic
    print("\n📁 events/views.py:")
    try:
        with open('events/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'send_registration_approval_email' in content:
                print("   ✅ Uses combined email function")
            else:
                print("   ❌ May be using old email logic")
                if 'send_mail(' in content:
                    print("   ⚠️ Found direct send_mail() calls")
    except Exception as e:
        print(f"   ❌ Could not read views.py: {e}")
        
    # Check for vehicle pass URL issues
    print("\n🔍 VEHICLE PASS URL ANALYSIS:")
    print("From logs: Bad Request: /vehicle-pass/generate/4306/-/")
    print("Issue: Vehicle number is '-' which causes 400 error")
    print("Solution: Skip vehicle pass generation for invalid vehicle data")

if __name__ == "__main__":
    debug_email_flow()