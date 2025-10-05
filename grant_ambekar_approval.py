#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import ApprovalUser

print("Granting all level approval to Ambekar_mp...")

try:
    # Get the user
    user = User.objects.get(username='Ambekar_mp')
    
    # Make sure user has admin access
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    
    # Create or update ApprovalUser
    approval_user, created = ApprovalUser.objects.get_or_create(
        user=user,
        defaults={
            'state_code': 'MP',
            'is_super_approver': True,
            'is_state_approver': True,
            'is_district_approver': True,
            'is_upzone_approver': True,
            'allowed_registration_types': ['participant', 'volunteer', 'organization_representative'],
        }
    )
    
    if not created:
        # Update existing
        approval_user.state_code = 'MP'
        approval_user.is_super_approver = True
        approval_user.is_state_approver = True
        approval_user.is_district_approver = True
        approval_user.is_upzone_approver = True
        approval_user.allowed_registration_types = ['participant', 'volunteer', 'organization_representative']
        approval_user.save()
        print("✓ Updated approval permissions for Ambekar_mp")
    else:
        print("✓ Created super approver permissions for Ambekar_mp")
    
    print("\n🎉 Ambekar_mp now has:")
    print("- Super approver (all levels)")
    print("- District, UpZone, State approval rights")
    print("- All registration types (participant, volunteer, organization)")
    print("- Full admin panel access")
    
except User.DoesNotExist:
    print("❌ User 'Ambekar_mp' not found. Please create the user first.")