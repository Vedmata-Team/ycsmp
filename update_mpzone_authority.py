#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import ApprovalUser

def update_mpzone_authority():
    """Give state-level verification authority to MPZONE user"""
    
    try:
        # Find MPZONE user
        user = User.objects.get(username='MPZONE')
        print(f"Found user: {user.username} - {user.first_name}")
        
        # Get or create ApprovalUser
        approval_user, created = ApprovalUser.objects.get_or_create(
            user=user,
            defaults={
                'state_code': 'MP',
                'is_state_approver': True,
                'allowed_registration_types': ['participant', 'volunteer', 'organization_representative']
            }
        )
        
        if not created:
            # Update existing ApprovalUser
            approval_user.state_code = 'MP'
            approval_user.is_super_approver = False
            approval_user.is_state_approver = True
            approval_user.is_district_approver = False
            approval_user.is_upzone_approver = False
            approval_user.districts = []
            approval_user.upzone = None
            approval_user.allowed_registration_types = ['participant', 'volunteer', 'organization_representative']
            approval_user.save()
            print("Updated existing ApprovalUser record")
        else:
            print("Created new ApprovalUser record")
        
        # Ensure user has staff status
        if not user.is_staff:
            user.is_staff = True
            user.save()
            print("Granted staff access")
        
        print("\n✅ MPZONE Authority Updated:")
        print(f"Username: {user.username}")
        print(f"Name: {user.first_name}")
        print(f"Email: {user.email}")
        print(f"State Code: {approval_user.state_code}")
        print(f"State Approver: {approval_user.is_state_approver}")
        print(f"Registration Types: {approval_user.allowed_registration_types}")
        print(f"Assignment: {approval_user.get_assignment_display()}")
        
        return True
        
    except User.DoesNotExist:
        print("❌ User 'MPZONE' not found!")
        print("Available users with similar names:")
        similar_users = User.objects.filter(username__icontains='mp')
        for u in similar_users:
            print(f"- {u.username} ({u.first_name})")
        return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    update_mpzone_authority()