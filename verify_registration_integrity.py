#!/usr/bin/env python
"""
Final verification script to ensure all registration number issues are resolved
"""
import os
import sys
import django
from django.db.models import Count, Q

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration

def comprehensive_verification():
    """Comprehensive verification of registration number integrity"""
    print("=== COMPREHENSIVE REGISTRATION NUMBER VERIFICATION ===")
    
    issues_found = []
    
    # 1. Check for duplicate registration numbers
    print("\n1. Checking for duplicate registration numbers...")
    duplicates = {}
    all_registrations = EventRegistration.objects.filter(registration_number__isnull=False)
    
    for reg in all_registrations:
        if reg.registration_number in duplicates:
            duplicates[reg.registration_number].append(reg)
        else:
            duplicates[reg.registration_number] = [reg]
    
    actual_duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}
    
    if actual_duplicates:
        issues_found.append(f"Duplicate registration numbers: {len(actual_duplicates)}")
        print(f"❌ Found {len(actual_duplicates)} duplicate registration numbers:")
        for reg_number, registrations in actual_duplicates.items():
            print(f"  {reg_number}: {len(registrations)} registrations")
    else:
        print("✅ No duplicate registration numbers found")
    
    # 2. Check approved registrations without registration numbers
    print("\n2. Checking approved registrations without registration numbers...")
    approved_without_numbers = EventRegistration.objects.filter(
        approval_status='approved',
        registration_number__isnull=True
    )
    
    count = approved_without_numbers.count()
    if count > 0:
        issues_found.append(f"Approved registrations without numbers: {count}")
        print(f"❌ Found {count} approved registrations without registration numbers")
        for reg in approved_without_numbers[:5]:  # Show first 5
            print(f"  ID {reg.id}: {reg.full_name} ({reg.registration_type})")
        if count > 5:
            print(f"  ... and {count - 5} more")
    else:
        print("✅ All approved registrations have registration numbers")
    
    # 3. Check registration number format consistency
    print("\n3. Checking registration number format consistency...")
    format_issues = []
    
    for reg in all_registrations:
        reg_num = reg.registration_number
        reg_type = reg.registration_type
        
        # Expected prefixes
        expected_prefixes = {
            'participant': 'YCS-',
            'volunteer': 'YCSV-',
            'organization_representative': 'YCSO-'
        }
        
        expected_prefix = expected_prefixes.get(reg_type, 'YCS-')
        
        if not reg_num.startswith(expected_prefix):
            format_issues.append({
                'id': reg.id,
                'name': reg.full_name,
                'type': reg_type,
                'number': reg_num,
                'expected_prefix': expected_prefix
            })
    
    if format_issues:
        issues_found.append(f"Format inconsistencies: {len(format_issues)}")
        print(f"❌ Found {len(format_issues)} registration numbers with format issues:")
        for issue in format_issues[:5]:  # Show first 5
            print(f"  ID {issue['id']}: {issue['number']} (expected {issue['expected_prefix']}...)")
        if len(format_issues) > 5:
            print(f"  ... and {len(format_issues) - 5} more")
    else:
        print("✅ All registration numbers follow correct format")
    
    # 4. Check for null/empty registration numbers in wrong states
    print("\n4. Checking for null registration numbers in wrong approval states...")
    wrong_state_nulls = EventRegistration.objects.filter(
        Q(approval_status__in=['district_approved', 'upzone_approved']) &
        Q(registration_number__isnull=True)
    )
    
    count = wrong_state_nulls.count()
    if count > 0:
        issues_found.append(f"Partially approved without numbers: {count}")
        print(f"⚠️  Found {count} partially approved registrations without numbers")
    else:
        print("✅ No partially approved registrations missing numbers")
    
    # 5. Statistics by registration type
    print("\n5. Registration statistics by type:")
    type_stats = EventRegistration.objects.values('registration_type').annotate(
        total=Count('id'),
        pending=Count('id', filter=Q(approval_status='pending')),
        district_approved=Count('id', filter=Q(approval_status='district_approved')),
        upzone_approved=Count('id', filter=Q(approval_status='upzone_approved')),
        approved=Count('id', filter=Q(approval_status='approved')),
        rejected=Count('id', filter=Q(approval_status='rejected')),
        with_reg_number=Count('registration_number')
    )
    
    for stat in type_stats:
        reg_type = stat['registration_type']
        print(f"\n  {reg_type.upper()}:")
        print(f"    Total: {stat['total']}")
        print(f"    Pending: {stat['pending']}")
        print(f"    District Approved: {stat['district_approved']}")
        print(f"    UpZone Approved: {stat['upzone_approved']}")
        print(f"    Final Approved: {stat['approved']}")
        print(f"    Rejected: {stat['rejected']}")
        print(f"    With Reg Number: {stat['with_reg_number']}")
        
        # Check if approved count matches reg number count
        if stat['approved'] != stat['with_reg_number']:
            diff = stat['approved'] - stat['with_reg_number']
            if diff > 0:
                print(f"    ⚠️  {diff} approved registrations missing reg numbers")
    
    # 6. Summary
    print(f"\n=== VERIFICATION SUMMARY ===")
    if issues_found:
        print(f"❌ Issues found:")
        for issue in issues_found:
            print(f"  - {issue}")
        print(f"\nTotal issue categories: {len(issues_found)}")
        return False
    else:
        print("✅ All registration number integrity checks passed!")
        print("✅ No issues found in the system")
        return True

def generate_health_report():
    """Generate a health report for registration numbers"""
    print("\n=== REGISTRATION NUMBER HEALTH REPORT ===")
    
    total_registrations = EventRegistration.objects.count()
    with_reg_numbers = EventRegistration.objects.filter(registration_number__isnull=False).count()
    approved_registrations = EventRegistration.objects.filter(approval_status='approved').count()
    
    print(f"Total Registrations: {total_registrations}")
    print(f"With Registration Numbers: {with_reg_numbers}")
    print(f"Approved Registrations: {approved_registrations}")
    
    if approved_registrations > 0:
        coverage = (with_reg_numbers / approved_registrations) * 100
        print(f"Registration Number Coverage: {coverage:.1f}%")
        
        if coverage >= 100:
            print("✅ Perfect coverage - all approved registrations have numbers")
        elif coverage >= 95:
            print("✅ Excellent coverage")
        elif coverage >= 90:
            print("⚠️  Good coverage but some issues remain")
        else:
            print("❌ Poor coverage - significant issues remain")
    
    # Check uniqueness
    unique_numbers = EventRegistration.objects.filter(
        registration_number__isnull=False
    ).values('registration_number').distinct().count()
    
    if unique_numbers == with_reg_numbers:
        print("✅ All registration numbers are unique")
    else:
        duplicates = with_reg_numbers - unique_numbers
        print(f"❌ {duplicates} duplicate registration numbers detected")

if __name__ == "__main__":
    print("Starting comprehensive verification...")
    
    # Run verification
    success = comprehensive_verification()
    
    # Generate health report
    generate_health_report()
    
    if success:
        print(f"\n🎉 VERIFICATION PASSED - System is healthy!")
    else:
        print(f"\n⚠️  VERIFICATION FAILED - Issues need to be addressed")
    
    print("\nVerification complete!")