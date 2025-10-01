#!/usr/bin/env python
import os
import sys
import django
from collections import defaultdict
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration

def find_duplicates():
    """Find duplicate registrations based on gender, name, date_of_birth, state, district"""
    
    # Group registrations by duplicate criteria
    duplicate_groups = defaultdict(list)
    
    # Get all registrations
    all_registrations = EventRegistration.objects.all().order_by('registration_date')
    
    for registration in all_registrations:
        # Create key based on duplicate criteria
        key = (
            registration.gender.lower() if registration.gender else '',
            registration.full_name.lower().strip(),
            registration.date_of_birth,
            registration.state.lower().strip() if registration.state else '',
            registration.city.lower().strip() if registration.city else ''
        )
        
        duplicate_groups[key].append(registration)
    
    # Filter groups that have duplicates
    duplicates = {key: regs for key, regs in duplicate_groups.items() if len(regs) > 1}
    
    return duplicates

def display_duplicates(duplicates):
    """Display all duplicate users"""
    
    if not duplicates:
        print("No duplicate registrations found.")
        return 0
    
    total_duplicates = 0
    same_type_groups = 0
    multiple_type_groups = 0
    
    print("=" * 80)
    print("DUPLICATE REGISTRATIONS FOUND")
    print("=" * 80)
    
    for i, (key, registrations) in enumerate(duplicates.items(), 1):
        gender, name, dob, state, district = key
        
        # Check if registrations are in same type or multiple types
        reg_types = set(reg.registration_type for reg in registrations)
        is_multiple_types = len(reg_types) > 1
        
        if is_multiple_types:
            multiple_type_groups += 1
            type_info = f"MULTIPLE TYPES: {', '.join(reg_types)}"
        else:
            same_type_groups += 1
            type_info = f"SAME TYPE: {list(reg_types)[0]} (registered {len(registrations)} times)"
        
        print(f"\nGroup {i}: {type_info}")
        print(f"  Gender: {gender.title()}")
        print(f"  Name: {name.title()}")
        print(f"  Date of Birth: {dob}")
        print(f"  State: {state.title()}")
        print(f"  District: {district.title()}")
        print(f"  Found {len(registrations)} registrations:")
        
        for j, reg in enumerate(registrations, 1):
            print(f"    {j}. ID: {reg.id} | Type: {reg.get_registration_type_display()} | "
                  f"Event: {reg.event.title} | Registered: {reg.registration_date.strftime('%Y-%m-%d %H:%M')} | "
                  f"Status: {reg.get_approval_status_display()}")
        
        total_duplicates += len(registrations) - 1  # Keep one, count others as duplicates
    
    print(f"\n" + "=" * 80)
    print(f"SUMMARY:")
    print(f"Users registered in same type multiple times: {same_type_groups}")
    print(f"Users registered in multiple types: {multiple_type_groups}")
    print(f"Total duplicate registrations to be removed: {total_duplicates}")
    return total_duplicates

def delete_duplicates(duplicates):
    """Delete duplicate registrations, keeping the latest one"""
    
    deleted_count = 0
    
    for key, registrations in duplicates.items():
        # Sort by registration_date (latest first)
        sorted_regs = sorted(registrations, key=lambda x: x.registration_date, reverse=True)
        
        # Keep the latest one, delete the rest
        to_keep = sorted_regs[0]
        to_delete = sorted_regs[1:]
        
        reg_types = set(reg.registration_type for reg in registrations)
        type_info = "multiple types" if len(reg_types) > 1 else f"same type ({list(reg_types)[0]})"
        
        print(f"\nProcessing group: {key[1].title()} ({type_info})")
        print(f"  Keeping: ID {to_keep.id} - {to_keep.get_registration_type_display()} (registered on {to_keep.registration_date.strftime('%Y-%m-%d %H:%M')})")
        
        for reg in to_delete:
            print(f"  Deleting: ID {reg.id} - {reg.get_registration_type_display()} (registered on {reg.registration_date.strftime('%Y-%m-%d %H:%M')})")
            reg.delete()
            deleted_count += 1
    
    return deleted_count

def main():
    print("Duplicate Registration Removal Tool")
    print("=" * 50)
    
    # Find duplicates
    print("Scanning for duplicate registrations...")
    duplicates = find_duplicates()
    
    # Display duplicates
    total_duplicates = display_duplicates(duplicates)
    
    if total_duplicates == 0:
        return
    
    # Ask admin for confirmation
    print("\n" + "=" * 80)
    choice = input(f"Do you want to delete {total_duplicates} duplicate registrations? (Y/N): ").strip().upper()
    
    if choice == 'Y':
        print("\nDeleting duplicate registrations...")
        deleted_count = delete_duplicates(duplicates)
        print(f"\nSuccessfully deleted {deleted_count} duplicate registrations.")
        print("Latest registration kept for each duplicate group.")
    elif choice == 'N':
        print("\nOperation aborted. No registrations were deleted.")
    else:
        print("\nInvalid choice. Operation aborted.")

if __name__ == "__main__":
    main()