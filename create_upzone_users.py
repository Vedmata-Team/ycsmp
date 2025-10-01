#!/usr/bin/env python
import os
import sys
import django
import csv
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import ApprovalUser, UpZone

def create_upzone_users():
    """Create upzone level approvers"""
    
    # User data
    users_data = [
        {
            'name': 'RAJESH PATEL',
            'phone': '9425060396',
            'role': 'SAMANVAYAK-MP ZONE',
            'city': 'BHOPAL',
            'username': 'rajesh_samanvayak_mp',
            'password': 'Rajesh@2024'
        },
        {
            'name': 'PRABHAKANT TIWARI',
            'phone': '8770516798', 
            'role': 'SAH-SAMANVAYAK-- MP ZONE',
            'city': 'BHOPAL',
            'username': 'prabhakant_sah_samanvayak_mp',
            'password': 'Prabhakant@2024'
        },
        {
            'name': 'RC GAYAKWAD',
            'phone': '9425603584',
            'role': 'SAH-SAMANVAYAK-- MP ZONE', 
            'city': 'BHOPAL',
            'username': 'rc_gayakwad_sah_samanvayak_mp',
            'password': 'RcGayakwad@2024'
        }
    ]
    
    # Get or create a default upzone for MP
    upzone, created = UpZone.objects.get_or_create(
        name='MP Central Zone',
        defaults={
            'districts': ['Bhopal', 'Sehore', 'Raisen', 'Vidisha'],
            'is_active': True
        }
    )
    
    created_users = []
    existing_users = []
    
    for user_data in users_data:
        username = user_data['username']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            existing_users.append(username)
            continue
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                password=user_data['password'],
                first_name=user_data['name'],
                email=f"{username}@ycsmp.in",
                is_staff=True
            )
            
            # Create ApprovalUser with upzone level access
            approval_user = ApprovalUser.objects.create(
                user=user,
                state_code='MP',
                upzone=upzone,
                is_upzone_approver=True,
                allowed_registration_types=['participant', 'volunteer', 'organization_representative']
            )
            
            created_users.append({
                'name': user_data['name'],
                'phone': user_data['phone'],
                'role': user_data['role'],
                'username': username,
                'password': user_data['password'],
                'email': f"{username}@ycsmp.in"
            })
            
        except Exception as e:
            print(f"Error creating user {user_data['name']}: {e}")
    
    # Print results
    print(f"Created {len(created_users)} upzone users:")
    print("=" * 100)
    print(f"{'Name':<20} {'Phone':<12} {'Role':<25} {'Username':<30} {'Password':<15}")
    print("=" * 100)
    
    for user_info in created_users:
        print(f"{user_info['name']:<20} {user_info['phone']:<12} {user_info['role']:<25} {user_info['username']:<30} {user_info['password']:<15}")
    
    if existing_users:
        print(f"\n{len(existing_users)} users already exist:")
        for username in existing_users:
            print(f"- {username}")
    
    # Export to CSV
    if created_users:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"upzone_users_credentials_{timestamp}.csv"
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Name', 'Phone', 'Role', 'Username', 'Password', 'Email', 'Level', 'Registration_Types']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for user_info in created_users:
                writer.writerow({
                    'Name': user_info['name'],
                    'Phone': user_info['phone'],
                    'Role': user_info['role'],
                    'Username': user_info['username'],
                    'Password': user_info['password'],
                    'Email': user_info['email'],
                    'Level': 'UpZone Approver',
                    'Registration_Types': 'All Types'
                })
        
        print(f"\n📄 Credentials exported to: {csv_filename}")
    
    return created_users

if __name__ == "__main__":
    create_upzone_users()