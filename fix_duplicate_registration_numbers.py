#!/usr/bin/env python
"""
Fix duplicate registration numbers in the database
"""
import os
import sys
import django
from django.db import transaction

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration

def fix_duplicate_registration_numbers():
    """Fix all duplicate registration numbers"""
    print("Starting duplicate registration number fix...")
    
    # Find all registrations with duplicate registration numbers
    duplicates = {}
    all_registrations = EventRegistration.objects.filter(registration_number__isnull=False)
    
    for reg in all_registrations:
        if reg.registration_number in duplicates:
            duplicates[reg.registration_number].append(reg)
        else:
            duplicates[reg.registration_number] = [reg]
    
    # Filter only actual duplicates
    actual_duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}
    
    if not actual_duplicates:
        print("No duplicate registration numbers found!")
        return
    
    print(f"Found {len(actual_duplicates)} duplicate registration numbers affecting {sum(len(v) for v in actual_duplicates.values())} registrations")
    
    fixed_count = 0
    
    for reg_number, registrations in actual_duplicates.items():
        print(f"\nFixing duplicate registration number: {reg_number}")
        print(f"Found {len(registrations)} registrations with this number")
        
        # Keep the first one (usually oldest), fix the rest
        for i, reg in enumerate(registrations[1:], 1):
            try:
                with transaction.atomic():
                    # Generate new registration number
                    new_reg_number = reg.generate_registration_number()
                    old_reg_number = reg.registration_number
                    
                    reg.registration_number = new_reg_number
                    reg.save()
                    
                    print(f"  Fixed registration {reg.pk}: {old_reg_number} -> {new_reg_number}")
                    fixed_count += 1
                    
            except Exception as e:
                print(f"  Error fixing registration {reg.pk}: {e}")
                # Try with timestamp fallback
                try:
                    import datetime
                    import random
                    timestamp = int(datetime.datetime.now().timestamp() * 1000) % 100000
                    random_suffix = random.randint(10, 99)
                    state_code = reg.state_code or 'XX'
                    city_prefix = reg.city[:3].upper() if reg.city else 'XXX'
                    
                    if reg.registration_type == 'organization_representative':
                        base_prefix = 'YCSO'
                    elif reg.registration_type == 'volunteer':
                        base_prefix = 'YCSV'
                    else:
                        base_prefix = 'YCS'
                    
                    fallback_number = f"{base_prefix}-{state_code}-{city_prefix}-{timestamp}{random_suffix}"
                    reg.registration_number = fallback_number
                    reg.save()
                    
                    print(f"  Fixed with fallback registration {reg.pk}: {old_reg_number} -> {fallback_number}")
                    fixed_count += 1
                    
                except Exception as e2:
                    print(f"  Failed to fix registration {reg.pk} even with fallback: {e2}")
    
    print(f"\nFixed {fixed_count} duplicate registration numbers")

def check_for_remaining_duplicates():
    """Check if there are any remaining duplicates"""
    print("\nChecking for remaining duplicates...")
    
    duplicates = {}
    all_registrations = EventRegistration.objects.filter(registration_number__isnull=False)
    
    for reg in all_registrations:
        if reg.registration_number in duplicates:
            duplicates[reg.registration_number].append(reg)
        else:
            duplicates[reg.registration_number] = [reg]
    
    actual_duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}
    
    if actual_duplicates:
        print(f"WARNING: Still found {len(actual_duplicates)} duplicate registration numbers!")
        for reg_number, registrations in actual_duplicates.items():
            print(f"  {reg_number}: {len(registrations)} registrations")
    else:
        print("✓ No duplicate registration numbers found!")

if __name__ == "__main__":
    fix_duplicate_registration_numbers()
    check_for_remaining_duplicates()
    print("\nDuplicate registration number fix completed!")