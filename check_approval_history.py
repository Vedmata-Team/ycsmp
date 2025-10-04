#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration

def check_approval_history():
    """Check approval history and log details for volunteers and organization registrations"""
    
    # Get all volunteers and organization registrations
    registrations = EventRegistration.objects.filter(
        registration_type__in=['volunteer', 'organization_representative']
    ).order_by('-registration_date')
    
    print(f"Total volunteers and organization registrations: {registrations.count()}")
    print("="*80)
    
    for reg in registrations:
        print(f"\nName: {reg.full_name}")
        print(f"Type: {reg.get_registration_type_display()}")
        print(f"Current Status: {reg.approval_status}")
        print(f"Registration Date: {reg.registration_date}")
        
        # Check approval history
        print("Approval History:")
        if reg.district_approver:
            print(f"  District: {reg.district_approver.username} at {reg.district_approved_at}")
        else:
            print("  District: Not approved")
            
        if reg.upzone_approver:
            print(f"  Upzone: {reg.upzone_approver.username} at {reg.upzone_approved_at}")
        else:
            print("  Upzone: Not approved")
            
        if reg.final_approver:
            print(f"  Final: {reg.final_approver.username} at {reg.final_approved_at}")
        else:
            print("  Final: Not approved")
            
        if hasattr(reg, 'rejected_by') and reg.rejected_by:
            print(f"  Rejected: {reg.rejected_by.username} at {getattr(reg, 'rejected_at', 'N/A')}")
        
        print(f"Full History: {reg.get_approval_history()}")
        print("-" * 60)

if __name__ == "__main__":
    check_approval_history()