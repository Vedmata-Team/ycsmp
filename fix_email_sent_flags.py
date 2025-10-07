#!/usr/bin/env python3
"""
Fix Email Sent Flags
====================
Quick fix for email_sent flag inconsistencies
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration, EmailLog
from django.db import transaction

def fix_email_sent_flags():
    """Fix email_sent flags based on EmailLog data"""
    
    print("🔧 FIXING EMAIL_SENT FLAGS")
    print("=" * 40)
    
    # Get registrations with successful email logs
    successful_email_reg_ids = EmailLog.objects.filter(
        success=True,
        email_type='approval'
    ).values_list('registration_id', flat=True).distinct()
    
    print(f"Found {len(successful_email_reg_ids)} registrations with successful email logs")
    
    # Find registrations that need flag update (have successful email but flag is False)
    needs_update = EventRegistration.objects.filter(
        pk__in=successful_email_reg_ids,
        email_sent=False
    )
    
    count = needs_update.count()
    print(f"Registrations needing email_sent flag update: {count}")
    
    if count == 0:
        print("✅ All email_sent flags are already correct!")
        return
    
    # Show some examples
    print("\nExamples of registrations to be updated:")
    for reg in needs_update[:5]:
        print(f"  - {reg.full_name} ({reg.email}) - Reg#: {reg.registration_number}")
    
    if count > 5:
        print(f"  ... and {count - 5} more")
    
    response = input(f"\nUpdate email_sent=True for {count} registrations? (y/N): ").strip().lower()
    
    if response == 'y':
        try:
            with transaction.atomic():
                updated = needs_update.update(email_sent=True)
                print(f"✅ Successfully updated {updated} email_sent flags")
                
                # Verify the update
                remaining = EventRegistration.objects.filter(
                    pk__in=successful_email_reg_ids,
                    email_sent=False
                ).count()
                
                if remaining == 0:
                    print("✅ All flags are now consistent!")
                else:
                    print(f"⚠️ {remaining} flags still need attention")
                    
        except Exception as e:
            print(f"❌ Error updating flags: {e}")
    else:
        print("❌ Update cancelled")

def check_current_status():
    """Check current email_sent flag status"""
    
    print("📊 CURRENT EMAIL_SENT STATUS")
    print("=" * 40)
    
    approved_regs = EventRegistration.objects.filter(approval_status='approved')
    total = approved_regs.count()
    
    email_sent_true = approved_regs.filter(email_sent=True).count()
    email_sent_false = approved_regs.filter(email_sent=False).count()
    
    print(f"Total approved registrations: {total}")
    print(f"Email sent = True: {email_sent_true} ({email_sent_true/total*100:.1f}%)")
    print(f"Email sent = False: {email_sent_false} ({email_sent_false/total*100:.1f}%)")
    
    # Check successful email logs
    successful_logs = EmailLog.objects.filter(
        success=True,
        email_type='approval'
    ).values_list('registration_id', flat=True).distinct().count()
    
    print(f"Successful email logs: {successful_logs}")
    print()

if __name__ == "__main__":
    check_current_status()
    fix_email_sent_flags()
    print("\n" + "="*40)
    check_current_status()