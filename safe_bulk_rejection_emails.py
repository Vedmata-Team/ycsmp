#!/usr/bin/env python
"""
Safe bulk rejection email sender - prevents spam and errors
"""
import os
import sys
import django
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration, EmailLog
from events.email_utils import send_registration_approval_email

def send_bulk_rejection_emails():
    """Send rejection emails to all rejected registrations safely"""
    print("=== SAFE BULK REJECTION EMAIL SENDER ===")
    
    # Get all rejected registrations without rejection emails
    rejected_regs = EventRegistration.objects.filter(approval_status='rejected')
    
    # Filter out those who already received rejection emails
    unsent_rejections = []
    for reg in rejected_regs:
        rejection_email_sent = EmailLog.objects.filter(
            registration=reg,
            email_type='rejection',
            success=True
        ).exists()
        
        if not rejection_email_sent:
            unsent_rejections.append(reg)
    
    total = len(unsent_rejections)
    print(f"Total rejected registrations needing emails: {total}")
    
    if total == 0:
        print("✅ All rejected registrations have already received emails!")
        return
    
    # Safety limits
    BATCH_SIZE = 50  # Process 50 at a time
    DELAY_BETWEEN_EMAILS = 3  # 3 seconds between emails
    DELAY_BETWEEN_BATCHES = 60  # 1 minute between batches
    
    print(f"Processing in batches of {BATCH_SIZE} with {DELAY_BETWEEN_EMAILS}s delay between emails")
    print(f"Estimated time: {(total * DELAY_BETWEEN_EMAILS + (total // BATCH_SIZE) * DELAY_BETWEEN_BATCHES) // 60} minutes")
    
    proceed = input(f"Send rejection emails to {total} registrations? (y/N): ").lower().strip()
    if proceed != 'y':
        print("Operation cancelled.")
        return
    
    sent = 0
    failed = 0
    
    # Process in batches
    for batch_num in range(0, total, BATCH_SIZE):
        batch = unsent_rejections[batch_num:batch_num + BATCH_SIZE]
        batch_size = len(batch)
        
        print(f"\n--- BATCH {batch_num // BATCH_SIZE + 1} ({batch_size} emails) ---")
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        
        for i, reg in enumerate(batch):
            try:
                print(f"Sending {batch_num + i + 1}/{total}: {reg.full_name} ({reg.email})")
                
                if send_registration_approval_email(reg):
                    reg.email_sent = True
                    reg.save(update_fields=['email_sent'])
                    sent += 1
                    print(f"  ✓ Sent successfully")
                else:
                    failed += 1
                    print(f"  ✗ Failed to send")
                
                # Delay between emails (except last email in batch)
                if i < batch_size - 1:
                    print(f"  Waiting {DELAY_BETWEEN_EMAILS} seconds...")
                    time.sleep(DELAY_BETWEEN_EMAILS)
                    
            except Exception as e:
                failed += 1
                print(f"  ✗ Error: {e}")
                time.sleep(2)  # Extra delay on error
        
        # Progress update
        print(f"Batch {batch_num // BATCH_SIZE + 1} completed: {sent} sent, {failed} failed")
        
        # Delay between batches (except last batch)
        if batch_num + BATCH_SIZE < total:
            print(f"Waiting {DELAY_BETWEEN_BATCHES} seconds before next batch...")
            time.sleep(DELAY_BETWEEN_BATCHES)
    
    print(f"\n=== FINAL SUMMARY ===")
    print(f"Total processed: {total}")
    print(f"Successfully sent: {sent}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(sent/total*100):.1f}%" if total > 0 else "0%")
    print(f"Completed at: {datetime.now().strftime('%H:%M:%S')}")

def show_rejection_stats():
    """Show rejection email statistics"""
    print("=== REJECTION EMAIL STATISTICS ===")
    
    total_rejected = EventRegistration.objects.filter(approval_status='rejected').count()
    rejection_emails_sent = EmailLog.objects.filter(email_type='rejection', success=True).count()
    rejection_emails_failed = EmailLog.objects.filter(email_type='rejection', success=False).count()
    
    print(f"Total rejected registrations: {total_rejected}")
    print(f"Rejection emails sent successfully: {rejection_emails_sent}")
    print(f"Rejection emails failed: {rejection_emails_failed}")
    print(f"Pending rejection emails: {total_rejected - rejection_emails_sent}")
    
    if total_rejected > 0:
        coverage = (rejection_emails_sent / total_rejected) * 100
        print(f"Email coverage: {coverage:.1f}%")

if __name__ == "__main__":
    show_rejection_stats()
    send_bulk_rejection_emails()