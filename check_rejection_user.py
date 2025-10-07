#!/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration
from django.contrib.auth.models import User

def find_rejection_user(phone):
    """Find who rejected a registration by phone number"""
    try:
        registration = EventRegistration.objects.get(phone=phone)
        
        print(f"Registration Details:")
        print(f"Name: {registration.full_name}")
        print(f"Phone: {registration.phone}")
        print(f"City: {registration.city}")
        print(f"State: {registration.state}")
        print(f"Status: {registration.approval_status}")
        
        if registration.approval_status == 'rejected':
            if hasattr(registration, 'rejected_by') and registration.rejected_by:
                rejector = registration.rejected_by
                print(f"Rejected by: {rejector.get_full_name() or rejector.username}")
                print(f"User ID: {rejector.id}")
                print(f"Username: {rejector.username}")
                if hasattr(registration, 'rejected_at') and registration.rejected_at:
                    print(f"Rejected at: {registration.rejected_at}")
                if registration.rejection_reason:
                    print(f"Reason: {registration.rejection_reason}")
            else:
                print("Rejected by: Unknown (rejected_by field is empty)")
        else:
            print(f"Status is not rejected, it's: {registration.approval_status}")
            
    except EventRegistration.DoesNotExist:
        print(f"No registration found with phone number: {phone}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    phone = "9610290010"
    find_rejection_user(phone)