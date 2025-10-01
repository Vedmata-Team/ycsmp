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
from events.models import EventRegistration, ApprovalUser
from django.db import models

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

def create_district_users():
    """Create district users for each MP district with participant approval access"""
    
    # Get all unique MP districts
    mp_districts = EventRegistration.objects.filter(
        models.Q(state__icontains='madhya pradesh') |
        models.Q(state__iexact='MP')
    ).values_list('city', flat=True).distinct().order_by('city')
    
    mp_districts = [d for d in mp_districts if d and d.strip()]
    
    created_users = []
    existing_users = []
    
    for district in mp_districts:
        # Create username: district_mp_approver (lowercase, no spaces)
        username = f"{district.lower().replace(' ', '_').replace('-', '_')}_mp_approver"
        
        # Generate random password
        password = generate_random_password(district)
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            existing_users.append(username)
            continue
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=f"{district} District Approver",
                email=f"{username}@ycsmp.in",
                is_staff=True
            )
            
            # Create ApprovalUser
            approval_user = ApprovalUser.objects.create(
                user=user,
                state_code='MP',
                districts=[district],
                is_district_approver=True,
                allowed_registration_types=['participant']
            )
            
            created_users.append({
                'district': district,
                'username': username,
                'password': password,
                'email': f"{username}@ycsmp.in"
            })
            
        except Exception as e:
            print(f"Error creating user for {district}: {e}")
    
    # Print results
    print(f"Created {len(created_users)} district users:")
    print("=" * 80)
    print(f"{'District':<20} {'Username':<30} {'Password':<15} {'Email'}")
    print("=" * 80)
    
    for user_info in created_users:
        print(f"{user_info['district']:<20} {user_info['username']:<30} {user_info['password']:<15} {user_info['email']}")
    
    if existing_users:
        print(f"\n{len(existing_users)} users already exist:")
        for username in existing_users:
            print(f"- {username}")
    
    print(f"\nTotal MP Districts: {len(mp_districts)}")
    print(f"Created: {len(created_users)}")
    print(f"Already Existed: {len(existing_users)}")
    
    # Export to CSV
    if created_users:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"district_users_credentials_{timestamp}.csv"
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['District', 'Username', 'Password', 'Email', 'Role', 'Registration_Types']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for user_info in created_users:
                writer.writerow({
                    'District': user_info['district'],
                    'Username': user_info['username'],
                    'Password': user_info['password'],
                    'Email': user_info['email'],
                    'Role': 'District Approver',
                    'Registration_Types': 'Participant Only'
                })
        
        print(f"\n📄 Credentials exported to: {csv_filename}")
    
    return created_users

if __name__ == "__main__":
    create_district_users()