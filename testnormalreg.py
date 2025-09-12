#!/usr/bin/env python
import os
import sys

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')

import django
django.setup()

from events.forms import EventRegistrationForm

def test_normal_registration_form():
    """Test normal registration form validation"""
    print("Testing EventRegistrationForm (normal registration)...")
    
    # Test data for normal registration (matching actual form)
    test_data = {
        'full_name': 'Test User',
        'phone': '9876543210',
        'email': 'test@example.com',
        'date_of_birth': '1990-01-01',
        'gender': 'M',  # Correct choice: M, F, O
        'transport_mode': 'bus',
        'previous_shivir': False,
        'education': 'graduation',  # Correct choice from EDUCATION_CHOICES
        'occupation': 'Student',
        'village_taluka': 'Test Village',
        'country': 'India',
        'state': 'Madhya Pradesh',
        'city': 'Bhopal',
        'arrival_date': '2025-10-26',  # Required field from ARRIVAL_DATE_CHOICES
        'campaigns': ['youth_connect', 'health'],  # Correct choices from CAMPAIGN_CHOICES
        'special_skills': ['technology'],  # Correct choice from SPECIAL_SKILLS_CHOICES
        'interested_in_volunteering': False,
    }
    
    try:
        print("1. Creating form instance...")
        form = EventRegistrationForm(data=test_data)
        
        print("2. Checking form validity...")
        is_valid = form.is_valid()
        print(f"Form is valid: {is_valid}")
        
        if not is_valid:
            print("\nForm validation errors:")
            for field, errors in form.errors.items():
                print(f"  {field}: {errors}")
            
            if form.non_field_errors():
                print(f"  Non-field errors: {form.non_field_errors()}")
        else:
            print("\nForm validation passed! No errors found.")
            
        # Test with minimal data
        print("\n3. Testing with minimal required data...")
        minimal_data = {
            'full_name': 'Test User',
            'phone': '9876543210',
            'email': 'test@example.com',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'transport_mode': 'bus',
            'previous_shivir': False,
            'education': 'graduation',
            'village_taluka': 'Test Village',
            'country': 'India',
            'state': 'Madhya Pradesh',
            'city': 'Bhopal',
            'arrival_date': '2025-10-26',  # Required field
            'campaigns': ['youth_connect', 'health'],
            'interested_in_volunteering': False,
        }
        
        minimal_form = EventRegistrationForm(data=minimal_data)
        minimal_valid = minimal_form.is_valid()
        print(f"Minimal form is valid: {minimal_valid}")
        
        if not minimal_valid:
            print("Minimal form errors:")
            for field, errors in minimal_form.errors.items():
                print(f"  {field}: {errors}")
        
        # Test form field requirements
        print("\n4. Testing form field requirements...")
        form_instance = EventRegistrationForm()
        required_fields = []
        for field_name, field in form_instance.fields.items():
            if field.required:
                required_fields.append(field_name)
        
        print(f"Required fields: {required_fields}")
        
        # Test with empty data to see all required field errors
        print("\n5. Testing with empty data to see all validation errors...")
        empty_form = EventRegistrationForm(data={})
        empty_valid = empty_form.is_valid()
        print(f"Empty form is valid: {empty_valid}")
        
        if not empty_valid:
            print("Empty form errors (showing required fields):")
            for field, errors in empty_form.errors.items():
                print(f"  {field}: {errors}")
            
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_normal_registration_form()