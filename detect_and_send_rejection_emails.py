#!/usr/bin/env python3
"""
Send Rejection Emails (Based on send_pending_emails.py logic)
============================================================
Sends rejection emails to rejected users who haven't received them
"""

import os
import sys
import django
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration
from events.email_utils import send_registration_approval_email

def send_rejection_emails():
    """Send rejection emails to rejected users without emails (same logic as send_pending_emails.py)"""
    
    # Find rejected users who haven't received emails (SAME LOGIC as send_pending_emails.py)
    pending_rejection_users = EventRegistration.objects.filter(
        approval_status='rejected',  # Only rejected users
        email_sent=False,           # Haven't received emails
        email__isnull=False         # Have valid email
    ).exclude(email='')             # Exclude empty emails
    
    total = pending_rejection_users.count()
    
    if total == 0:
        print("✅ No pending rejection emails to send")
        return True
    
    print(f"📧 Found {total} rejected users without emails")
    print("=" * 50)
    
    sent_count = 0
    failed_count = 0
    
    for i, registration in enumerate(pending_rejection_users):
        current = i + 1
        print(f"\n[{current}/{total}] Processing: {registration.full_name}")
        print(f"Email: {registration.email}")
        print(f"ID: {registration.id}")
        print(f"Location: {registration.city}, {registration.state}")
        
        # Show rejection details
        if hasattr(registration, 'rejected_by') and registration.rejected_by:
            print(f"Rejected by: {registration.rejected_by.get_full_name() or registration.rejected_by.username}")
        
        try:
            # Send rejection email (SAME LOGIC as send_pending_emails.py)
            success = send_registration_approval_email(registration)
            
            if success:
                # Mark as sent (SAME LOGIC as send_pending_emails.py)
                registration.email_sent = True
                registration.save(update_fields=['email_sent'])
                sent_count += 1
                print(f"✅ Rejection email sent successfully")
            else:
                failed_count += 1
                print(f"❌ Rejection email failed")
                
        except Exception as e:
            failed_count += 1
            print(f"❌ Error: {str(e)}")
        
        # Small delay between emails (SAME as send_pending_emails.py)
        if current < total:
            time.sleep(1)
    
    # Final summary (SAME LOGIC as send_pending_emails.py)
    print("\n" + "=" * 50)
    print("📊 Rejection Email Sending Summary")
    print("=" * 50)
    print(f"Total processed: {total}")
    print(f"✅ Successfully sent: {sent_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"Success rate: {(sent_count/total)*100:.1f}%")
    
    if sent_count > 0:
        print(f"\n🎉 {sent_count} rejection emails sent successfully!")
    
    return failed_count == 0

def show_pending_rejection_users():
    """Show rejected users who need emails (preview mode)"""
    
    pending_rejection_users = EventRegistration.objects.filter(
        approval_status='rejected',
        email_sent=False,
        email__isnull=False
    ).exclude(email='')
    
    total = pending_rejection_users.count()
    
    if total == 0:
        print("✅ No rejected users need emails")
        return
    
    print(f"📋 REJECTED USERS NEEDING EMAILS: {total}")
    print("=" * 70)
    
    for i, user in enumerate(pending_rejection_users[:20], 1):  # Show first 20
        rejected_by = getattr(user, 'rejected_by', None)
        rejected_at = getattr(user, 'rejected_at', None)
        
        print(f"{i:2d}. {user.full_name} ({user.email})")
        print(f"    ID: {user.id} | {user.city}, {user.state}")
        if rejected_by:
            print(f"    Rejected by: {rejected_by.get_full_name() or rejected_by.username}")
        if rejected_at:
            print(f"    Rejected at: {rejected_at.strftime('%d/%m/%Y %H:%M')}")
        print()
    
    if total > 20:
        print(f"... and {total - 20} more users")
    print()

def main():
    """Main execution function (same pattern as send_pending_emails.py)"""
    
    print("🚀 REJECTION EMAIL SENDER")
    print("=" * 60)
    
    # Show menu
    print("1. Preview rejected users needing emails")
    print("2. Send rejection emails")
    print("3. Exit")
    print()
    
    choice = input("Select option (1-3): ").strip()
    
    if choice == '1':
        show_pending_rejection_users()
    elif choice == '2':
        success = send_rejection_emails()
        sys.exit(0 if success else 1)
    elif choice == '3':
        print("👋 Goodbye!")
        sys.exit(0)
    else:
        print("❌ Invalid choice")
        sys.exit(1)

if __name__ == "__main__":
    main()