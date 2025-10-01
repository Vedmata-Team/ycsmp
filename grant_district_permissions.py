#!/usr/bin/env python
import os
import sys
import django
import csv

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from events.models import EventRegistration, ApprovalUser

def grant_district_permissions():
    """Grant necessary permissions to district users from CSV"""
    
    # Read usernames from CSV
    csv_file = 'updated_district_passwords_20251001_153931.csv'
    usernames = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                usernames.append(row['Username'])
    except FileNotFoundError:
        print(f"CSV file {csv_file} not found. Using fallback method...")
        # Get all district approvers from database
        district_approvers = ApprovalUser.objects.filter(is_district_approver=True)
        usernames = [au.user.username for au in district_approvers]
    
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
                approval_user.is_district_approver = True
                approval_user.state_code = 'MP'
                if not approval_user.allowed_registration_types:
                    approval_user.allowed_registration_types = ['participant']
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
    print(f"✅ Permissions granted to {len(updated_users)} district users:")
    print("=" * 80)
    
    for user_info in updated_users:
        print(f"Username: {user_info['username']}")
        print(f"Name: {user_info['name']}")
        print(f"Staff Status: {user_info['is_staff']}")
        print(f"Permissions: {', '.join(user_info['permissions'])}")
        print("-" * 80)
    
    return updated_users

if __name__ == "__main__":
    grant_district_permissions()