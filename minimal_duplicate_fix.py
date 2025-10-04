#!/usr/bin/env python
"""
Minimal fix - only prevent duplicates, keep existing logic intact
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration
from django.db import transaction

def minimal_duplicate_fix():
    """Fix only the immediate duplicate issue"""
    print("Applying minimal duplicate fix...")
    
    # Find duplicates
    duplicates = {}
    all_regs = EventRegistration.objects.filter(registration_number__isnull=False)
    
    for reg in all_regs:
        if reg.registration_number in duplicates:
            duplicates[reg.registration_number].append(reg)
        else:
            duplicates[reg.registration_number] = [reg]
    
    actual_duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}
    
    if not actual_duplicates:
        print("✅ No duplicates found!")
        return
    
    print(f"Found {len(actual_duplicates)} duplicate numbers")
    
    # Fix only duplicates, keep first one unchanged
    for reg_number, registrations in actual_duplicates.items():
        print(f"Fixing: {reg_number}")
        
        # Keep first registration unchanged
        keep_reg = registrations[0]
        print(f"  Keeping: ID {keep_reg.id} - {keep_reg.full_name}")
        
        # Fix others by adding suffix
        for i, reg in enumerate(registrations[1:], 1):
            try:
                with transaction.atomic():
                    # Simple suffix approach - minimal change
                    new_number = f"{reg_number}-{i}"
                    
                    # Ensure it's unique
                    while EventRegistration.objects.filter(registration_number=new_number).exists():
                        new_number = f"{reg_number}-{i}-{i}"
                        i += 1
                    
                    reg.registration_number = new_number
                    reg.save()
                    
                    print(f"  Fixed: ID {reg.id} -> {new_number}")
                    
            except Exception as e:
                print(f"  Error fixing ID {reg.id}: {e}")

if __name__ == "__main__":
    minimal_duplicate_fix()
    print("Minimal fix completed!")