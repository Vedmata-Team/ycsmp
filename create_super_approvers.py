#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import ApprovalUser, EventRegistration

# User data with special characters
users_data = [
    {'name': 'AMAR DHAKAD', 'phone': '8319440752', 'special_char': '@'},
    {'name': 'PANKESH GHODKI', 'phone': '8305135501', 'special_char': '#'},
    {'name': 'GOVIND VISHWAKARMA', 'phone': '6267421109', 'special_char': '$'},
    {'name': 'ABHISHEK PARMAR', 'phone': '9669270021', 'special_char': '%'},
]

print("Creating super approvers...")

for user_data in users_data:
    name = user_data['name']
    phone = user_data['phone']
    special_char = user_data['special_char']
    
    # Create username: firstname_mp
    first_name = name.split()[0].lower()
    username = f"{first_name}_mp"
    
    # Create password: Firstname123[special_char]
    password = f"{first_name.capitalize()}123{special_char}"
    
    # Create or get user
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': name.split()[0],
            'last_name': ' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
            'is_staff': True,
            'is_active': True,
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"✓ Created user: {name}")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
    else:
        # Update password for existing user
        user.set_password(password)
        user.save()
        print(f"✓ User exists, updated password: {name}")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
    
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
        print(f"  ✓ Updated approval permissions")
    else:
        print(f"  ✓ Created super approver permissions")
    
    print()

print("🎉 All super approvers created successfully!")
print("\nLogin Summary:")
print("=" * 50)
for user_data in users_data:
    name = user_data['name']
    first_name = name.split()[0].lower()
    username = f"{first_name}_mp"
    password = f"{first_name.capitalize()}123{user_data['special_char']}"
    print(f"{name}:")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print()

print("Permissions granted:")
print("- Super approver (all levels)")
print("- District, UpZone, State approval rights")
print("- All registration types (participant, volunteer, organization)")
print("- Admin panel access")