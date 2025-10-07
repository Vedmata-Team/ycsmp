#!/usr/bin/env python3
"""
Comprehensive Rejection Email Sender
===================================
Sends rejection emails to rejected registrations with safety checks
"""

import os
import sys
import django
from django.db import transaction
from django.utils import timezone
from datetime import datetime
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration, EmailLog
from events.email_utils import send_registration_approval_email

class RejectionEmailSender:
    def __init__(self):
        self.total_rejected = 0
        self.emails_sent = 0
        self.emails_failed = 0
        self.already_sent = 0
        
    def analyze_rejected_registrations(self):
        """Analyze rejected registrations and email status"""
        print("📊 REJECTION EMAIL ANALYSIS")
        print("=" * 50)
        
        # Get all rejected registrations
        rejected_regs = EventRegistration.objects.filter(approval_status='rejected')
        self.total_rejected = rejected_regs.count()
        
        print(f"Total rejected registrations: {self.total_rejected}")
        
        if self.total_rejected == 0:
            print("✅ No rejected registrations found!")
            return []
        
        # Check email status
        with_email_sent_true = rejected_regs.filter(email_sent=True).count()
        with_email_sent_false = rejected_regs.filter(email_sent=False).count()
        
        print(f"With email_sent=True: {with_email_sent_true}")
        print(f"With email_sent=False: {with_email_sent_false}")
        
        # Check EmailLog for rejection emails
        rejection_email_logs = EmailLog.objects.filter(
            email_type='rejection',
            success=True
        ).values_list('registration_id', flat=True).distinct()
        
        rejection_logs_count = len(rejection_email_logs)
        print(f"Successful rejection email logs: {rejection_logs_count}")
        
        # Find registrations needing emails
        needs_email = []
        
        for reg in rejected_regs:
            # Check if rejection email was logged as successful
            has_rejection_log = reg.id in rejection_email_logs
            
            if not has_rejection_log:
                needs_email.append(reg)
        
        print(f"Registrations needing rejection emails: {len(needs_email)}")
        print()
        
        return needs_email
    
    def show_sample_registrations(self, registrations, count=10):
        """Show sample registrations that need emails"""
        if not registrations:
            return
            
        print(f"📋 SAMPLE REGISTRATIONS (showing first {min(count, len(registrations))}):")
        print("-" * 70)
        
        for i, reg in enumerate(registrations[:count]):
            rejected_by = getattr(reg, 'rejected_by', None)
            rejected_at = getattr(reg, 'rejected_at', None)
            
            print(f"{i+1:2d}. {reg.full_name} ({reg.email})")
            print(f"    ID: {reg.id} | {reg.city}, {reg.state}")
            print(f"    Type: {reg.get_registration_type_display()}")
            if rejected_by:
                print(f"    Rejected by: {rejected_by.get_full_name() or rejected_by.username}")
            if rejected_at:
                print(f"    Rejected at: {rejected_at.strftime('%d/%m/%Y %H:%M')}")
            if hasattr(reg, 'rejection_reason') and reg.rejection_reason:
                reason = reg.rejection_reason[:50] + "..." if len(reg.rejection_reason) > 50 else reg.rejection_reason
                print(f"    Reason: {reason}")
            print()
        
        if len(registrations) > count:
            print(f"... and {len(registrations) - count} more registrations")
        print()
    
    def send_rejection_emails(self, registrations, batch_size=20):
        """Send rejection emails in batches"""
        if not registrations:
            print("✅ No rejection emails to send!")
            return
        
        total = len(registrations)
        print(f"🚀 SENDING REJECTION EMAILS")
        print(f"Total to process: {total}")
        print(f"Batch size: {batch_size}")
        print("=" * 50)
        
        # Confirm before sending
        response = input(f"Send rejection emails to {total} registrations? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Operation cancelled")
            return
        
        # Process in batches
        for i in range(0, total, batch_size):
            batch = registrations[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            print(f"\n📦 BATCH {batch_num} (Records {i+1}-{min(i+batch_size, total)})")
            print("-" * 40)
            
            self._process_batch(batch)
            
            # Progress update
            processed = min(i + batch_size, total)
            progress = (processed / total) * 100
            print(f"Progress: {processed}/{total} ({progress:.1f}%)")
            
            # Delay between batches
            if i + batch_size < total:
                print("Waiting 3 seconds before next batch...")
                time.sleep(3)
        
        self._print_final_summary()
    
    def _process_batch(self, batch):
        """Process a single batch of registrations"""
        for reg in batch:
            try:
                # Send rejection email
                if send_registration_approval_email(reg):
                    # Update email_sent flag
                    EventRegistration.objects.filter(pk=reg.pk).update(email_sent=True)
                    self.emails_sent += 1
                    print(f"✅ {reg.full_name} ({reg.email})")
                else:
                    self.emails_failed += 1
                    print(f"❌ {reg.full_name} ({reg.email}) - Email failed")
                
                # Small delay between emails
                time.sleep(0.5)
                
            except Exception as e:
                self.emails_failed += 1
                print(f"❌ {reg.full_name} ({reg.email}) - Error: {e}")
                time.sleep(1)
    
    def _print_final_summary(self):
        """Print final execution summary"""
        print(f"\n🎉 REJECTION EMAIL SENDING COMPLETED")
        print("=" * 50)
        print(f"Total rejected registrations: {self.total_rejected}")
        print(f"Emails sent successfully: {self.emails_sent}")
        print(f"Email failures: {self.emails_failed}")
        print(f"Success rate: {(self.emails_sent/(self.emails_sent+self.emails_failed)*100):.1f}%" if (self.emails_sent + self.emails_failed) > 0 else "N/A")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def send_test_rejection_email(self, email_address="divymohan.awgp@gmail.com"):
        """Send a test rejection email"""
        print(f"📧 SENDING TEST REJECTION EMAIL to {email_address}")
        print("-" * 50)
        
        # Get any rejected registration for template
        rejected_reg = EventRegistration.objects.filter(approval_status='rejected').first()
        
        if not rejected_reg:
            print("❌ No rejected registrations found for testing")
            return
        
        # Create test registration object
        class TestRegistration:
            def __init__(self, base_reg):
                self.full_name = "टेस्ट यूजर"
                self.phone = "9999999999"
                self.email = email_address
                self.registration_type = base_reg.registration_type
                self.state = base_reg.state
                self.city = base_reg.city
                self.approval_status = 'rejected'
                self.rejection_reason = "यह एक टेस्ट ईमेल है। कृपया इसे अनदेखा करें।"
                self.event = base_reg.event
                self.id = 99999
            
            def get_registration_type_display(self):
                type_map = {
                    'participant': 'प्रतिभागी',
                    'volunteer': 'समयदानी कार्यकर्ता',
                    'organization_representative': 'संगठन प्रतिनिधि'
                }
                return type_map.get(self.registration_type, self.registration_type)
            
            def get_profile_url(self):
                return f"/profile/{self.phone}_{self.full_name.replace(' ', '_')}/"
        
        test_reg = TestRegistration(rejected_reg)
        
        try:
            if send_registration_approval_email(test_reg):
                print(f"✅ Test rejection email sent successfully to {email_address}")
            else:
                print(f"❌ Failed to send test rejection email to {email_address}")
        except Exception as e:
            print(f"❌ Error sending test email: {e}")

def main():
    """Main execution function"""
    sender = RejectionEmailSender()
    
    print("🚀 REJECTION EMAIL SENDER")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Show menu
    while True:
        print("📋 MENU OPTIONS:")
        print("1. Analyze rejected registrations")
        print("2. Send rejection emails")
        print("3. Send test rejection email")
        print("4. Exit")
        print()
        
        choice = input("Select option (1-4): ").strip()
        
        if choice == '1':
            registrations = sender.analyze_rejected_registrations()
            sender.show_sample_registrations(registrations)
            
        elif choice == '2':
            registrations = sender.analyze_rejected_registrations()
            if registrations:
                sender.show_sample_registrations(registrations, 5)
                sender.send_rejection_emails(registrations)
            
        elif choice == '3':
            email = input("Enter test email address (default: divymohan.awgp@gmail.com): ").strip()
            if not email:
                email = "divymohan.awgp@gmail.com"
            sender.send_test_rejection_email(email)
            
        elif choice == '4':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-4.")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()