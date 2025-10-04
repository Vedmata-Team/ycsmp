#!/usr/bin/env python
"""
Test current registration number generation without making changes
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration

def test_current_logic():
    """Test current registration number generation"""
    print("Testing current registration number logic...")
    
    # Get a sample registration
    sample_reg = EventRegistration.objects.filter(
        registration_number__isnull=False
    ).first()
    
    if sample_reg:
        print(f"Sample existing number: {sample_reg.registration_number}")
        print(f"Registration type: {sample_reg.registration_type}")
        print(f"City: {sample_reg.city}")
        print(f"State: {sample_reg.state}")
        
        # Test generation without saving
        try:
            # Create a test registration object (not saved)
            test_reg = EventRegistration(
                registration_type=sample_reg.registration_type,
                city=sample_reg.city,
                state=sample_reg.state,
                full_name="Test User",
                phone="9999999999",
                email="test@test.com"
            )
            
            # Test number generation
            test_number = test_reg.generate_registration_number()
            print(f"Generated test number: {test_number}")
            print("✅ Generation logic working correctly")
            
        except Exception as e:
            print(f"❌ Error in generation: {e}")
    else:
        print("No existing registrations found to test with")

if __name__ == "__main__":
    test_current_logic()