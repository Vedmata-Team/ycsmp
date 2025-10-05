#!/usr/bin/env python
"""
Find rejected registrations that haven't received rejection emails
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration, EmailLog
from events.email_utils import send_registration_approval_email

def find_unsent_rejection_emails():
    """Find rejected registrations without rejection emails"""
    print("Finding rejected registrations without rejection emails...")
    
    # Get all rejected registrations
    rejected_regs = EventRegistration.objects.filter(approval_status='rejected')
    print(f"Total rejected registrations: {rejected_regs.count()}")
    
    # Find those without rejection email logs
    unsent_rejections = []
    
    for reg in rejected_regs:
        # Check if rejection email was sent
        rejection_email_sent = EmailLog.objects.filter(
            registration=reg,
            email_type='rejection',
            success=True
        ).exists()
        
        if not rejection_email_sent:
            unsent_rejections.append(reg)
    
    print(f"Rejected registrations without rejection emails: {len(unsent_rejections)}")
    
    if unsent_rejections:
        print("\nList of registrations needing rejection emails:")
        for reg in unsent_rejections[:10]:  # Show first 10
            print(f"- ID {reg.id}: {reg.full_name} ({reg.email}) - {reg.city}, {reg.state}")
        
        if len(unsent_rejections) > 10:
            print(f"... and {len(unsent_rejections) - 10} more")
        
        # Ask if user wants to send emails
        send_emails = input(f"\nSend rejection emails to {len(unsent_rejections)} registrations? (y/N): ").lower().strip()
        
        if send_emails == 'y':
            send_bulk_rejection_emails(unsent_rejections)
    else:
        print("✅ All rejected registrations have received rejection emails!")

def send_bulk_rejection_emails(registrations):
    """Send rejection emails in batches"""
    import time
    
    total = len(registrations)
    sent = 0
    failed = 0
    
    print(f"Sending rejection emails to {total} registrations...")
    
    for i, reg in enumerate(registrations):
        try:
            if send_registration_approval_email(reg):
                sent += 1
                print(f"✓ Sent to {reg.full_name} ({reg.email})")
            else:
                failed += 1
                print(f"✗ Failed to send to {reg.full_name} ({reg.email})")
            
            # Add delay every 10 emails
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{total}... waiting 3 seconds")
                time.sleep(3)
                
        except Exception as e:
            failed += 1
            print(f"✗ Error sending to {reg.full_name}: {e}")
            time.sleep(1)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total: {total}")
    print(f"Sent: {sent}")
    print(f"Failed: {failed}")

def show_email_stats():
    """Show email statistics"""
    print("\n=== EMAIL STATISTICS ===")
    
    total_logs = EmailLog.objects.count()
    approval_emails = EmailLog.objects.filter(email_type='approval').count()
    rejection_emails = EmailLog.objects.filter(email_type='rejection').count()
    successful_emails = EmailLog.objects.filter(success=True).count()
    failed_emails = EmailLog.objects.filter(success=False).count()
    
    print(f"Total email logs: {total_logs}")
    print(f"Approval emails: {approval_emails}")
    print(f"Rejection emails: {rejection_emails}")
    print(f"Successful: {successful_emails}")
    print(f"Failed: {failed_emails}")
    
    # Recent activity
    from django.utils import timezone
    from datetime import timedelta
    
    last_24h = timezone.now() - timedelta(hours=24)
    recent_emails = EmailLog.objects.filter(sent_at__gte=last_24h).count()
    print(f"Emails sent in last 24 hours: {recent_emails}")

if __name__ == "__main__":
    show_email_stats()
    find_unsent_rejection_emails()