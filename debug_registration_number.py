#!/usr/bin/env python3
"""
Debug script for registration number generation issue
"""

import os
import sys
import django
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration

def debug_registration_number():
    print("🔍 Debugging Registration Number Generation...")
    
    # Find registrations with approved status but no registration number
    approved_without_number = EventRegistration.objects.filter(
        approval_status='approved',
        registration_number__isnull=True
    )
    
    print(f"📊 Found {approved_without_number.count()} approved registrations without registration number")
    
    if approved_without_number.exists():
        print("\n🔧 Attempting to fix...")
        for reg in approved_without_number[:5]:  # Fix first 5
            print(f"Processing: {reg.full_name} (ID: {reg.id})")
            try:
                # Generate registration number
                reg_number = reg.generate_registration_number()
                print(f"  Generated: {reg_number}")
                
                # Update the registration
                reg.registration_number = reg_number
                reg.is_confirmed = True
                reg.save(update_fields=['registration_number', 'is_confirmed'])
                
                print(f"  ✅ Updated successfully")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    # Test registration number generation for different types
    print("\n🧪 Testing registration number generation...")
    
    test_cases = [
        {'city': 'Bhopal', 'state': 'Madhya Pradesh', 'type': 'participant'},
        {'city': 'Indore', 'state': 'Madhya Pradesh', 'type': 'volunteer'},
        {'city': 'Gwalior', 'state': 'Madhya Pradesh', 'type': 'organization_representative'},
    ]
    
    for case in test_cases:
        try:
            # Create a test registration object (don't save)
            test_reg = EventRegistration(
                city=case['city'],
                state=case['state'],
                registration_type=case['type'],
                full_name='Test User',
                email='test@example.com',
                phone='1234567890',
                date_of_birth='1990-01-01',
                gender='M',
                transport_mode='car',
                education='graduation',
                village_taluka='Test Village',
                arrival_date='2025-10-25',
                selected_campaigns=['youth_connect'],
                approval_status='approved'
            )
            
            reg_number = test_reg.generate_registration_number()
            print(f"  {case['type']} in {case['city']}: {reg_number}")
            
        except Exception as e:
            print(f"  ❌ Error for {case['type']} in {case['city']}: {e}")
    
    # Check recent registrations
    print("\n📋 Recent approved registrations:")
    recent = EventRegistration.objects.filter(
        approval_status='approved'
    ).order_by('-final_approved_at')[:10]
    
    for reg in recent:
        status = "✅" if reg.registration_number else "❌"
        print(f"  {status} {reg.full_name} - {reg.registration_number or 'NO NUMBER'}")

if __name__ == '__main__':
    debug_registration_number()