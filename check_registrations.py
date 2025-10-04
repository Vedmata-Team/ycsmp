#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration

def check_registrations():
    """Check all volunteer and organization registrations by status"""
    
    # Get all volunteers and organization registrations
    all_registrations = EventRegistration.objects.filter(
        registration_type__in=['volunteer', 'organization_representative']
    )
    
    print(f"Total volunteers and organization registrations: {all_registrations.count()}")
    print("\nBreakdown by status:")
    
    statuses = ['pending', 'district_approved', 'upzone_approved', 'approved', 'rejected']
    
    for status in statuses:
        count = all_registrations.filter(approval_status=status).count()
        print(f"  {status}: {count}")
    
    print("\nDetailed view of first 10 registrations:")
    for reg in all_registrations[:10]:
        upzone_history = "Yes" if (reg.upzone_approver and reg.upzone_approved_at) else "No"
        print(f"  {reg.full_name} | {reg.approval_status} | Upzone History: {upzone_history}")

if __name__ == "__main__":
    check_registrations()