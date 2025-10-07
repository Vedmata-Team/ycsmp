#!/usr/bin/env python3
"""
Email Sent Status Diagnostic Script
==================================
Check the current state of email_sent flags and identify inconsistencies
"""

import os
import django
from django.db.models import Q

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration, EmailLog

def check_email_sent_status():
    """Check email_sent flag status and identify issues"""
    
    print("📧 EMAIL SENT STATUS DIAGNOSTIC")
    print("=" * 60)
    
    # Get approved registrations
    approved_regs = EventRegistration.objects.filter(approval_status='approved')
    total_approved = approved_regs.count()
    
    # Check email_sent flags
    email_sent_true = approved_regs.filter(email_sent=True).count()
    email_sent_false = approved_regs.filter(email_sent=False).count()
    email_sent_null = approved_regs.filter(email_sent__isnull=True).count()
    
    print(f"Total approved registrations: {total_approved}")
    print(f"Email sent = True: {email_sent_true}")
    print(f"Email sent = False: {email_sent_false}")
    print(f"Email sent = NULL: {email_sent_null}")
    print()
    
    # Check against EmailLog
    print("📊 EMAIL LOG ANALYSIS")
    print("-" * 40)
    
    # Get successful email logs
    successful_emails = EmailLog.objects.filter(
        success=True,
        email_type='approval'
    ).values_list('registration_id', flat=True).distinct()
    
    successful_count = len(successful_emails)
    print(f"Successful emails in EmailLog: {successful_count}")
    
    # Find mismatches
    print("\n🔍 MISMATCH ANALYSIS")
    print("-" * 40)
    
    # Registrations with successful email logs but email_sent=False
    mismatch_1 = EventRegistration.objects.filter(
        pk__in=successful_emails,
        email_sent=False
    )
    
    print(f"Has successful email log but email_sent=False: {mismatch_1.count()}")
    
    # Registrations with email_sent=True but no successful email log
    mismatch_2 = EventRegistration.objects.filter(
        approval_status='approved',
        email_sent=True
    ).exclude(pk__in=successful_emails)
    
    print(f"Has email_sent=True but no successful email log: {mismatch_2.count()}")
    
    # Show details of mismatches
    if mismatch_1.exists():
        print(f"\n⚠️ REGISTRATIONS NEEDING email_sent FLAG UPDATE:")
        print("-" * 50)
        for reg in mismatch_1[:10]:  # Show first 10
            print(f"ID: {reg.id} | {reg.full_name} | {reg.email} | Reg#: {reg.registration_number}")
        
        if mismatch_1.count() > 10:
            print(f"... and {mismatch_1.count() - 10} more")
    
    # Check registrations without registration numbers
    print(f"\n🔢 REGISTRATION NUMBER ANALYSIS")
    print("-" * 40)
    
    approved_no_reg_num = EventRegistration.objects.filter(
        approval_status='approved'
    ).filter(
        Q(registration_number__isnull=True) | Q(registration_number__exact='')
    ).count()
    
    print(f"Approved without registration number: {approved_no_reg_num}")
    
    return {
        'total_approved': total_approved,
        'email_sent_true': email_sent_true,
        'email_sent_false': email_sent_false,
        'successful_emails': successful_count,
        'mismatch_needs_update': mismatch_1.count(),
        'approved_no_reg_num': approved_no_reg_num
    }

def fix_email_sent_flags():
    """Fix email_sent flags based on EmailLog data"""
    
    print("\n🔧 FIXING EMAIL_SENT FLAGS")
    print("=" * 40)
    
    # Get successful email logs
    successful_emails = EmailLog.objects.filter(
        success=True,
        email_type='approval'
    ).values_list('registration_id', flat=True).distinct()
    
    # Find registrations that need flag update
    needs_update = EventRegistration.objects.filter(
        pk__in=successful_emails,
        email_sent=False
    )
    
    count = needs_update.count()
    
    if count == 0:
        print("✅ No email_sent flags need updating")
        return
    
    response = input(f"Update email_sent=True for {count} registrations? (y/N): ").strip().lower()
    
    if response == 'y':
        updated = needs_update.update(email_sent=True)
        print(f"✅ Updated {updated} email_sent flags")
    else:
        print("❌ Update cancelled")

def main():
    """Main execution"""
    stats = check_email_sent_status()
    
    if stats['mismatch_needs_update'] > 0:
        print(f"\n⚠️ Found {stats['mismatch_needs_update']} registrations with email_sent flag issues")
        fix_email_sent_flags()
    else:
        print("\n✅ All email_sent flags are consistent with EmailLog data")
    
    # Final summary
    print(f"\n📋 SUMMARY")
    print("-" * 20)
    print(f"Total approved: {stats['total_approved']}")
    print(f"Email flags correct: {stats['email_sent_true']}")
    print(f"Email logs successful: {stats['successful_emails']}")
    print(f"Missing reg numbers: {stats['approved_no_reg_num']}")

if __name__ == "__main__":
    main()