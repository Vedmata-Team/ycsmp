#!/usr/bin/env python
import os
import django
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration
from django.contrib.auth.models import User

def bulk_approve_volunteers_and_orgs():
    """Bulk approve pending and upzone_approved volunteers and organization registrations at district level"""
    
    # Get a superuser to perform the approvals
    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        print("No superuser found!")
        return
    
    # Get pending and upzone_approved volunteers and organization registrations (exclude rejected ones)
    target_registrations = EventRegistration.objects.filter(
        approval_status__in=['pending', 'upzone_approved'],
        registration_type__in=['volunteer', 'organization_representative']
    ).exclude(approval_status='rejected')
    
    print(f"Found {target_registrations.count()} volunteers and organization registrations to process")
    
    updated_count = 0
    
    for registration in target_registrations:
        # Check if this registration was previously upzone approved
        has_upzone_history = registration.upzone_approver is not None and registration.upzone_approved_at is not None
        
        if has_upzone_history:
            # If it was upzone approved before, keep it at upzone level
            registration.approval_status = 'upzone_approved'
            # Ensure district approval is also set
            if not registration.district_approver:
                registration.district_approver = superuser
            if not registration.district_approved_at:
                registration.district_approved_at = timezone.now()
            print(f"✓ Maintained upzone level: {registration.full_name} (has upzone history)")
        else:
            # If no upzone history, set to district approved
            registration.approval_status = 'district_approved'
            registration.district_approver = superuser
            registration.district_approved_at = timezone.now()
            print(f"✓ District approved: {registration.full_name} (no upzone history)")
        
        registration.save()
        updated_count += 1
    
    print(f"\n🎉 Successfully district approved {updated_count} registrations!")
    print(f"Registration types: volunteers and organization representatives")

if __name__ == "__main__":
    bulk_approve_volunteers_and_orgs()