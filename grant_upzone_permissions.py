#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from events.models import EventRegistration, ApprovalUser

def grant_upzone_permissions():
    """Grant necessary permissions to upzone users"""
    
    usernames = [
        'rajesh_samanvayak_mp',
        'prabhakant_sah_samanvayak_mp', 
        'rc_gayakwad_sah_samanvayak_mp',
        'MPZONE'
    ]
    
    # Get required permissions
    registration_ct = ContentType.objects.get_for_model(EventRegistration)
    
    required_permissions = [
        'view_eventregistration',
        'change_eventregistration',
        'add_eventregistration',
    ]
    
    updated_users = []
    
    for username in usernames:
        try:
            user = User.objects.get(username=username)
            
            # Ensure user is staff
            user.is_staff = True
            user.save()
            
            # Grant permissions
            for perm_codename in required_permissions:
                try:
                    permission = Permission.objects.get(
                        codename=perm_codename,
                        content_type=registration_ct
                    )
                    user.user_permissions.add(permission)
                except Permission.DoesNotExist:
                    print(f"Permission {perm_codename} not found")
            
            # Update ApprovalUser if exists
            try:
                approval_user = ApprovalUser.objects.get(user=user)
                if username == 'MPZONE':
                    # MPZONE gets state-level authority
                    approval_user.is_state_approver = True
                    approval_user.is_upzone_approver = False
                    approval_user.is_district_approver = False
                else:
                    # Others get upzone-level authority
                    approval_user.is_upzone_approver = True
                    approval_user.is_state_approver = False
                    approval_user.is_district_approver = False
                approval_user.state_code = 'MP'
                approval_user.allowed_registration_types = ['participant', 'volunteer', 'organization_representative']
                approval_user.save()
            except ApprovalUser.DoesNotExist:
                print(f"ApprovalUser not found for {username}")
            
            updated_users.append({
                'username': username,
                'name': user.first_name,
                'is_staff': user.is_staff,
                'permissions': list(user.user_permissions.values_list('codename', flat=True))
            })
            
        except User.DoesNotExist:
            print(f"User {username} not found")
    
    # Print results
    print("✅ Permissions granted to MP zone users:")
    print("=" * 60)
    
    for user_info in updated_users:
        print(f"Username: {user_info['username']}")
        print(f"Name: {user_info['name']}")
        print(f"Staff Status: {user_info['is_staff']}")
        print(f"Permissions: {', '.join(user_info['permissions'])}")
        print("-" * 60)
    
    return updated_users

if __name__ == "__main__":
    grant_upzone_permissions()