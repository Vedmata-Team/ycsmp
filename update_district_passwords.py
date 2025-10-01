#!/usr/bin/env python
import os
import sys
import django
import csv
import random
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import ApprovalUser

def generate_random_password(district_name):
    """Generate random password with varying capitalization and special chars"""
    # Random capitalization patterns
    caps_patterns = [
        lambda s: s.capitalize(),  # First letter
        lambda s: s.upper(),       # All upper
        lambda s: s.lower(),       # All lower
        lambda s: ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(s)),  # Alternate
        lambda s: ''.join(c.upper() if random.choice([True, False]) else c.lower() for c in s)  # Random each
    ]
    
    # Special characters to choose from
    special_chars = ['@', '#', '$', '%', '&', '*', '!', '+']
    
    # Apply random capitalization
    district_part = random.choice(caps_patterns)(district_name.replace(' ', '').replace('-', ''))
    
    # Random special character
    special_char = random.choice(special_chars)
    
    # Random digits (keep 123 base but can modify)
    digits = '123'
    
    return f"{district_part}{special_char}{digits}"

def update_district_passwords():
    """Update passwords for all existing district approvers"""
    
    # Get all district approvers for MP
    district_approvers = ApprovalUser.objects.filter(
        state_code='MP',
        is_district_approver=True
    )
    
    updated_users = []
    
    for approval_user in district_approvers:
        user = approval_user.user
        
        # Get district name from districts list
        if approval_user.districts:
            district = approval_user.districts[0]  # Take first district
            
            # Generate new random password
            new_password = generate_random_password(district)
            
            # Update user password
            user.set_password(new_password)
            user.save()
            
            updated_users.append({
                'district': district,
                'username': user.username,
                'password': new_password,
                'email': user.email,
                'first_name': user.first_name
            })
    
    # Print results
    print(f"Updated passwords for {len(updated_users)} district users:")
    print("=" * 80)
    print(f"{'District':<20} {'Username':<30} {'New Password':<15} {'Email'}")
    print("=" * 80)
    
    for user_info in updated_users:
        print(f"{user_info['district']:<20} {user_info['username']:<30} {user_info['password']:<15} {user_info['email']}")
    
    # Export to CSV
    if updated_users:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"updated_district_passwords_{timestamp}.csv"
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['District', 'Username', 'Password', 'Email', 'Role', 'Registration_Types']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for user_info in updated_users:
                writer.writerow({
                    'District': user_info['district'],
                    'Username': user_info['username'],
                    'Password': user_info['password'],
                    'Email': user_info['email'],
                    'Role': 'District Approver',
                    'Registration_Types': 'Participant Only'
                })
        
        print(f"\n📄 Updated credentials exported to: {csv_filename}")
    
    return updated_users

if __name__ == "__main__":
    update_district_passwords()