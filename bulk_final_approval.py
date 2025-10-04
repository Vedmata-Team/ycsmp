#!/usr/bin/env python
import os
import django
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration
from django.contrib.auth.models import User

def bulk_final_approval():
    """Bulk final approval for volunteers and organization registrations"""
    
    # Get a superuser to perform the approvals
    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        print("No superuser found!")
        return
    
    # Get registrations that are ready for final approval:
    # - Currently district_approved or upzone_approved
    # - Volunteers or organization representatives
    # - Not rejected
    # - Not already finally approved
    
    ready_for_final = EventRegistration.objects.filter(
        approval_status__in=['district_approved', 'upzone_approved'],
        registration_type__in=['volunteer', 'organization_representative'],
        final_approver__isnull=True
    ).exclude(approval_status='rejected')
    
    print(f"Found {ready_for_final.count()} registrations ready for final approval")
    
    approved_count = 0
    
    for registration in ready_for_final:
        # Set to final approved status
        registration.approval_status = 'approved'
        registration.final_approver = superuser
        registration.final_approved_at = timezone.now()
        
        # Ensure all previous approval levels are set
        if not registration.district_approver:
            registration.district_approver = superuser
        if not registration.district_approved_at:
            registration.district_approved_at = timezone.now()
        
        registration.save()
        approved_count += 1
        
        print(f"✓ Final approved: {registration.full_name} ({registration.get_registration_type_display()})")
        print(f"  Email will be sent automatically with ID card")
    
    print(f"\n🎉 Successfully final approved {approved_count} registrations!")
    print("📧 Approval emails with ID cards will be sent automatically")

if __name__ == "__main__":
    bulk_final_approval()