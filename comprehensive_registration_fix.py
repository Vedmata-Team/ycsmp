#!/usr/bin/env python
"""
Comprehensive fix for duplicate registration numbers across all registration types
"""
import os
import sys
import django
from django.db import transaction
from django.db.models import Count

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration

def analyze_registration_numbers():
    """Analyze current registration number patterns"""
    print("=== REGISTRATION NUMBER ANALYSIS ===")
    
    # Count by registration type
    type_counts = EventRegistration.objects.values('registration_type').annotate(
        total=Count('id'),
        with_reg_number=Count('registration_number')
    )
    
    print("\nRegistration counts by type:")
    for item in type_counts:
        reg_type = item['registration_type']
        total = item['total']
        with_number = item['with_reg_number']
        without_number = total - with_number
        print(f"  {reg_type}: {total} total, {with_number} with reg number, {without_number} without")
    
    # Find duplicates
    duplicates = {}
    all_registrations = EventRegistration.objects.filter(registration_number__isnull=False)
    
    for reg in all_registrations:
        if reg.registration_number in duplicates:
            duplicates[reg.registration_number].append(reg)
        else:
            duplicates[reg.registration_number] = [reg]
    
    actual_duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}
    
    if actual_duplicates:
        print(f"\nFound {len(actual_duplicates)} duplicate registration numbers:")
        for reg_number, registrations in actual_duplicates.items():
            print(f"  {reg_number}: {len(registrations)} registrations")
            for reg in registrations:
                print(f"    - ID {reg.id}: {reg.full_name} ({reg.registration_type})")
    else:
        print("\n✓ No duplicate registration numbers found!")
    
    return actual_duplicates

def fix_all_registration_numbers():
    """Fix all registration number issues"""
    print("\n=== FIXING REGISTRATION NUMBERS ===")
    
    fixed_count = 0
    error_count = 0
    
    # First, find and fix duplicates
    duplicates = analyze_registration_numbers()
    
    if duplicates:
        print(f"\nFixing {len(duplicates)} duplicate registration numbers...")
        
        for reg_number, registrations in duplicates.items():
            print(f"\nProcessing duplicate: {reg_number}")
            
            # Keep the first one (usually oldest), fix the rest
            for i, reg in enumerate(registrations[1:], 1):
                try:
                    with transaction.atomic():
                        old_reg_number = reg.registration_number
                        
                        # Generate new registration number using the model method
                        new_reg_number = generate_unique_registration_number(reg)
                        
                        reg.registration_number = new_reg_number
                        reg.save()
                        
                        print(f"  ✓ Fixed ID {reg.id}: {old_reg_number} -> {new_reg_number}")
                        fixed_count += 1
                        
                except Exception as e:
                    print(f"  ✗ Error fixing ID {reg.id}: {e}")
                    error_count += 1
    
    # Now fix registrations without registration numbers (approved ones)
    print(f"\nFixing approved registrations without registration numbers...")
    
    approved_without_numbers = EventRegistration.objects.filter(
        approval_status='approved',
        registration_number__isnull=True
    )
    
    print(f"Found {approved_without_numbers.count()} approved registrations without numbers")
    
    for reg in approved_without_numbers:
        try:
            with transaction.atomic():
                new_reg_number = generate_unique_registration_number(reg)
                reg.registration_number = new_reg_number
                reg.is_confirmed = True
                reg.save()
                
                print(f"  ✓ Added number to ID {reg.id}: {new_reg_number}")
                fixed_count += 1
                
        except Exception as e:
            print(f"  ✗ Error adding number to ID {reg.id}: {e}")
            error_count += 1
    
    print(f"\n=== SUMMARY ===")
    print(f"Fixed: {fixed_count}")
    print(f"Errors: {error_count}")
    
    return fixed_count, error_count

def generate_unique_registration_number(registration):
    """Generate a unique registration number for a registration"""
    import datetime
    import random
    
    state_code = registration.state_code or 'XX'
    city_prefix = registration.city[:3].upper() if registration.city else 'XXX'
    
    # Different prefix for each registration type
    if registration.registration_type == 'volunteer':
        base_prefix = 'YCSV'
    elif registration.registration_type == 'organization_representative':
        base_prefix = 'YCSO'
    else:
        base_prefix = 'YCS'
    
    prefix = f"{base_prefix}-{state_code}-{city_prefix}-"
    
    # Try to use the model's method first
    try:
        return registration.generate_registration_number()
    except:
        # Fallback to timestamp-based generation
        timestamp = int(datetime.datetime.now().timestamp() * 1000) % 100000
        random_suffix = random.randint(10, 99)
        
        # Ensure uniqueness
        for attempt in range(10):
            candidate = f"{prefix}{timestamp}{random_suffix}"
            if not EventRegistration.objects.filter(registration_number=candidate).exists():
                return candidate
            random_suffix = random.randint(10, 99)
        
        # Final fallback
        return f"{prefix}{timestamp}{random.randint(100, 999)}"

def verify_fix():
    """Verify that all issues are fixed"""
    print("\n=== VERIFICATION ===")
    
    # Check for remaining duplicates
    duplicates = {}
    all_registrations = EventRegistration.objects.filter(registration_number__isnull=False)
    
    for reg in all_registrations:
        if reg.registration_number in duplicates:
            duplicates[reg.registration_number].append(reg)
        else:
            duplicates[reg.registration_number] = [reg]
    
    actual_duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}
    
    if actual_duplicates:
        print(f"❌ Still found {len(actual_duplicates)} duplicate registration numbers!")
        for reg_number, registrations in actual_duplicates.items():
            print(f"  {reg_number}: {len(registrations)} registrations")
        return False
    else:
        print("✅ No duplicate registration numbers found!")
    
    # Check approved registrations without numbers
    approved_without_numbers = EventRegistration.objects.filter(
        approval_status='approved',
        registration_number__isnull=True
    ).count()
    
    if approved_without_numbers > 0:
        print(f"❌ Found {approved_without_numbers} approved registrations without numbers!")
        return False
    else:
        print("✅ All approved registrations have registration numbers!")
    
    # Summary by type
    print("\nFinal summary by registration type:")
    type_counts = EventRegistration.objects.values('registration_type').annotate(
        total=Count('id'),
        approved=Count('id', filter=django.db.models.Q(approval_status='approved')),
        with_reg_number=Count('registration_number')
    )
    
    for item in type_counts:
        reg_type = item['registration_type']
        total = item['total']
        approved = item['approved']
        with_number = item['with_reg_number']
        print(f"  {reg_type}: {total} total, {approved} approved, {with_number} with reg number")
    
    return True

if __name__ == "__main__":
    print("Starting comprehensive registration number fix...")
    
    # Analyze current state
    analyze_registration_numbers()
    
    # Fix all issues
    fixed, errors = fix_all_registration_numbers()
    
    # Verify the fix
    success = verify_fix()
    
    if success:
        print(f"\n🎉 All registration number issues have been resolved!")
        print(f"Total fixes applied: {fixed}")
        if errors > 0:
            print(f"Errors encountered: {errors}")
    else:
        print(f"\n⚠️  Some issues may still remain. Please review the output above.")
    
    print("\nDone!")