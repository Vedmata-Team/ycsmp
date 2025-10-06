#!/usr/bin/env python3
"""
Test script to verify DOB validation is working correctly
Run this script to test the DOB validation system
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration
from datetime import datetime

def test_dob_validation():
    """Test DOB validation with actual database data"""
    print("🔍 Testing DOB Validation System...")
    print("=" * 50)
    
    # Get a sample registration
    registration = EventRegistration.objects.filter(approval_status='approved').first()
    
    if not registration:
        print("❌ No approved registrations found for testing")
        return
    
    print(f"📋 Testing with registration: {registration.full_name}")
    print(f"📞 Phone: {registration.phone}")
    print(f"🎂 Database DOB: {registration.date_of_birth}")
    print(f"🆔 Registration ID: {registration.id}")
    
    # Test different DOB formats
    test_cases = [
        {
            'name': 'Correct DOB (YYYY-MM-DD)',
            'dob': registration.date_of_birth.strftime('%Y-%m-%d'),
            'should_pass': True
        },
        {
            'name': 'Correct DOB (DD/MM/YYYY)', 
            'dob': registration.date_of_birth.strftime('%d/%m/%Y'),
            'should_pass': True
        },
        {
            'name': 'Wrong DOB',
            'dob': '1990-01-01',
            'should_pass': False
        },
        {
            'name': 'Invalid format',
            'dob': 'invalid-date',
            'should_pass': False
        }
    ]
    
    print("\n🧪 Running Test Cases:")
    print("-" * 30)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print(f"   Input: {test['dob']}")
        
        # Simulate validation logic
        try:
            if '/' in test['dob']:
                day, month, year = test['dob'].split('/')
                provided_date = datetime(int(year), int(month), int(day)).date()
            else:
                provided_date = datetime.strptime(test['dob'], '%Y-%m-%d').date()
            
            is_valid = provided_date == registration.date_of_birth
            
            if is_valid == test['should_pass']:
                print(f"   ✅ PASS - Validation {'succeeded' if is_valid else 'failed'} as expected")
            else:
                print(f"   ❌ FAIL - Expected {'success' if test['should_pass'] else 'failure'}, got {'success' if is_valid else 'failure'}")
                
        except (ValueError, AttributeError) as e:
            if not test['should_pass']:
                print(f"   ✅ PASS - Invalid format rejected as expected")
            else:
                print(f"   ❌ FAIL - Valid format rejected: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test URLs for manual verification:")
    print(f"ID Card: /id/card/{registration.id}/?dob={registration.date_of_birth.strftime('%Y-%m-%d')}")
    if registration.vehicle_number:
        print(f"Vehicle Pass: /vehicle-pass/generate/{registration.id}/{registration.vehicle_number}/?dob={registration.date_of_birth.strftime('%Y-%m-%d')}")
    
    print("\n💡 JavaScript validation test:")
    print(f"window.USER_DOB = '{registration.date_of_birth.strftime('%Y-%m-%d')}';")
    print("// This should be set in the template for proper validation")

if __name__ == '__main__':
    test_dob_validation()