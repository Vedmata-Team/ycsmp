#!/usr/bin/env python3
"""
Registration System Test Script
Tests the registration flow and identifies issues
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration, Event
from events.forms import EventRegistrationForm

def test_form_fields():
    """Test form field validation"""
    print("=== Testing Form Fields ===")
    
    form = EventRegistrationForm()
    print(f"Form fields: {list(form.fields.keys())}")
    
    # Test data
    test_data = {
        'full_name': 'Test User',
        'phone': '9876543210',
        'email': 'test@example.com',
        'date_of_birth': '1990-01-01',
        'gender': 'M',
        'transport_mode': 'car',
        'vehicle_number': 'MP01AB1234',
        'previous_shivir': True,
        'education': 'graduation',
        'occupation': 'Engineer',
        'village_taluka': 'Test Village',
        'country': 'India',
        'state': 'Madhya Pradesh',
        'city': 'Bhopal',
        'arrival_date': '2025-10-26',
        'interested_in_volunteering': False,
        'volunteering_details': '',
        'campaigns': ['youth_connect', 'water_cleanliness'],
        'special_skills': ['technology', 'teaching'],
        'special_skills_other': ''
    }
    
    form = EventRegistrationForm(data=test_data)
    print(f"Form is valid: {form.is_valid()}")
    if not form.is_valid():
        print(f"Form errors: {form.errors}")
    
    return form.is_valid()

def test_model_save():
    """Test model save functionality"""
    print("\n=== Testing Model Save ===")
    
    # Get or create an event
    event, created = Event.objects.get_or_create(
        title="Test Event",
        defaults={
            'description': 'Test Description',
            'category': 'Test',
            'venue': 'Test Venue',
            'event_date': '2025-10-26 10:00:00',
            'registration_deadline': '2025-10-25 23:59:59',
        }
    )
    
    # Create registration
    registration = EventRegistration(
        event=event,
        registration_type='participant',
        full_name='Test User',
        phone='9876543210',
        email='test@example.com',
        date_of_birth='1990-01-01',
        gender='M',
        transport_mode='car',
        vehicle_number='MP01AB1234',
        previous_shivir=True,
        education='graduation',
        occupation='Engineer',
        village_taluka='Test Village',
        country='India',
        state='Madhya Pradesh',
        city='Bhopal',
        arrival_date='2025-10-26',
        interested_in_volunteering=False,
        volunteering_details='',
        selected_campaigns=['youth_connect', 'water_cleanliness'],
        special_skills=['technology', 'teaching'],
        special_skills_other=''
    )
    
    try:
        registration.save()
        print(f"Registration saved successfully: ID {registration.id}")
        print(f"Campaigns: {registration.selected_campaigns}")
        print(f"Special Skills: {registration.special_skills}")
        return True
    except Exception as e:
        print(f"Error saving registration: {e}")
        return False

def test_view_logic():
    """Test view processing logic"""
    print("\n=== Testing View Logic ===")
    
    # Simulate POST data
    post_data = {
        'full_name': 'Test User',
        'phone': '9876543210',
        'email': 'test@example.com',
        'date_of_birth': '1990-01-01',
        'gender': 'M',
        'transport_mode': 'car',
        'vehicle_number': 'MP01AB1234',
        'previous_shivir': 'True',
        'education': 'graduation',
        'occupation': 'Engineer',
        'village_taluka': 'Test Village',
        'country': 'India',
        'state': 'Madhya Pradesh',
        'city': 'Bhopal',
        'arrival_date': '2025-10-26',
        'interested_in_volunteering': 'False',
        'volunteering_details': '',
        'campaigns': ['youth_connect', 'water_cleanliness'],
        'special_skills': ['technology', 'teaching'],
        'special_skills_other': ''
    }
    
    form = EventRegistrationForm(data=post_data)
    print(f"Form validation: {form.is_valid()}")
    
    if form.is_valid():
        print("✓ Form validation passed")
        
        # Test campaigns extraction
        campaigns = post_data.get('campaigns', [])
        special_skills = post_data.get('special_skills', [])
        
        print(f"✓ Campaigns extracted: {campaigns}")
        print(f"✓ Special skills extracted: {special_skills}")
        
        return True
    else:
        print(f"✗ Form validation failed: {form.errors}")
        return False

def main():
    """Run all tests"""
    print("Registration System Test")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("Form Fields", test_form_fields()))
    results.append(("Model Save", test_model_save()))
    results.append(("View Logic", test_view_logic()))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")

if __name__ == "__main__":
    main()