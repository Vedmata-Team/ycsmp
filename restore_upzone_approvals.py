#!/usr/bin/env python
import os
import django
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration
from django.contrib.auth.models import User

def restore_upzone_approvals():
    """Restore upzone approval status for registrations that were upzone approved before district approval"""
    
    # Get a superuser to perform the approvals
    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        print("No superuser found!")
        return
    
    # Find registrations that:
    # 1. Are currently district_approved
    # 2. Have upzone approval history (upzone_approver and upzone_approved_at exist)
    # 3. Upzone approval happened before district approval
    # 4. Are volunteers or organization representatives
    # 5. Don't have final approval yet
    
    candidates = EventRegistration.objects.filter(
        approval_status='district_approved',
        registration_type__in=['volunteer', 'organization_representative'],
        upzone_approver__isnull=False,
        upzone_approved_at__isnull=False,
        final_approver__isnull=True  # No final approval yet
    )
    
    print(f"Found {candidates.count()} candidates for upzone restoration")
    
    restored_count = 0
    
    for registration in candidates:
        # Check if upzone approval happened before district approval
        if (registration.upzone_approved_at and registration.district_approved_at and 
            registration.upzone_approved_at < registration.district_approved_at):
            
            # Restore to upzone_approved status
            registration.approval_status = 'upzone_approved'
            # Ensure district approval fields are preserved
            if not registration.district_approver:
                registration.district_approver = superuser
            if not registration.district_approved_at:
                registration.district_approved_at = timezone.now()
            
            registration.save()
            restored_count += 1
            
            print(f"✓ Restored to upzone: {registration.full_name}")
            print(f"  Upzone approved: {registration.upzone_approved_at}")
            print(f"  District approved: {registration.district_approved_at}")
            print(f"  Upzone approver: {registration.upzone_approver.username}")
            print("-" * 50)
    
    print(f"\n🎉 Successfully restored {restored_count} registrations to upzone level!")

if __name__ == "__main__":
    restore_upzone_approvals()