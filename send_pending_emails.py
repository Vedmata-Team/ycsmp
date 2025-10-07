#!/usr/bin/env python3
"""
Send emails to approved users who haven't received emails yet
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

def send_pending_emails():
    """Send emails to approved users without emails"""
    
    # Find approved users who haven't received emails
    pending_users = EventRegistration.objects.filter(
        approval_status='approved',
        email_sent=False,
        email__isnull=False
    ).exclude(email='')
    
    total = pending_users.count()
    
    if total == 0:
        print("✅ No pending emails to send")
        return True
    
    print(f"📧 Found {total} approved users without emails")
    print("=" * 50)
    
    sent_count = 0
    failed_count = 0
    
    for i, registration in enumerate(pending_users):
        current = i + 1
        print(f"\n[{current}/{total}] Processing: {registration.full_name}")
        print(f"Email: {registration.email}")
        
        try:
            # Send email
            success = send_registration_approval_email(registration)
            
            if success:
                # Mark as sent
                registration.email_sent = True
                registration.save(update_fields=['email_sent'])
                sent_count += 1
                print(f"✅ Email sent successfully")
            else:
                failed_count += 1
                print(f"❌ Email failed")
                
        except Exception as e:
            failed_count += 1
            print(f"❌ Error: {str(e)}")
        
        # Small delay between emails
        if current < total:
            time.sleep(1)
    
    # Final summary
    print("\n" + "=" * 50)
    print("📊 Email Sending Summary")
    print("=" * 50)
    print(f"Total processed: {total}")
    print(f"✅ Successfully sent: {sent_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"Success rate: {(sent_count/total)*100:.1f}%")
    
    if sent_count > 0:
        print(f"\n🎉 {sent_count} emails sent successfully!")
    
    return failed_count == 0

if __name__ == "__main__":
    success = send_pending_emails()
    sys.exit(0 if success else 1)