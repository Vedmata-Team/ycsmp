#!/usr/bin/env python
"""
Restore bulk rejected participant registrations to pending status
and send apology emails for technical issues
"""
import os
import sys
import django
import csv
from datetime import datetime
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration, EmailLog
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

def create_apology_email_template():
    """Create apology email template"""
    template_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #f8f9fa; padding: 20px; text-align: center; border-radius: 5px; }
        .content { padding: 20px 0; }
        .highlight { background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 15px 0; }
        .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>प्रान्तीय युवा चिंतन शिविर भोपाल 2025</h2>
            <h3>पंजीकरण स्थिति अपडेट</h3>
        </div>
        
        <div class="content">
            <p>प्रिय {{ registration.full_name }},</p>
            
            <p>नमस्कार!</p>
            
            <p>हमें खुशी है कि आपने <strong>प्रान्तीय युवा चिंतन शिविर भोपाल 2025</strong> के लिए पंजीकरण कराया है।</p>
            
            <div class="highlight">
                <p><strong>महत्वपूर्ण सूचना:</strong> पहले आपका पंजीकरण कुछ <strong>तकनीकी समस्याओं</strong> के कारण अस्वीकृत दिखाया गया था। हमें इसके लिए खेद है।</p>
            </div>
            
            <p><strong>अच्छी खबर:</strong> अब आपका पंजीकरण स्थिति <strong>प्रतीक्षारत</strong> है और हमारी टीम इसकी समीक्षा कर रही है।</p>
            
            <p><strong>आपकी पंजीकरण जानकारी:</strong></p>
            <ul>
                <li><strong>नाम:</strong> {{ registration.full_name }}</li>
                <li><strong>मोबाइल:</strong> {{ registration.phone }}</li>
                <li><strong>राज्य:</strong> {{ registration.state }}</li>
                <li><strong>जिला:</strong> {{ registration.city }}</li>
                <li><strong>वर्तमान स्थिति:</strong> प्रतीक्षारत</li>
            </ul>
            
            <p>हम जल्द ही आपको अंतिम स्थिति की जानकारी देंगे।</p>
            
            <p>असुविधा के लिए खेद और धन्यवाद!</p>
            
            <p><strong>युवा चिंतन शिविर टीम</strong><br>
            प्रान्तीय युवा चिंतन शिविर भोपाल 2025</p>
        </div>
        
        <div class="footer">
            <p>यह एक स्वचालित ईमेल है। कृपया इसका उत्तर न दें।</p>
            <p>अधिक जानकारी के लिए: <a href="https://ycsmp.in">ycsmp.in</a></p>
        </div>
    </div>
</body>
</html>
    """
    
    template_path = 'templates/events/emails/apology_email.html'
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    return template_path

def send_apology_email(registration):
    """Send apology email to registration"""
    try:
        subject = 'पंजीकरण स्थिति अपडेट - प्रान्तीय युवा चिंतन शिविर भोपाल 2025'
        
        context = {
            'registration': registration,
        }
        
        html_message = render_to_string('events/emails/apology_email.html', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[registration.email],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)
        
        # Log the email
        EmailLog.objects.create(
            registration=registration,
            email_type='apology',
            sent_by=None,  # System sent
            success=True
        )
        
        return True
        
    except Exception as e:
        print(f"❌ Email failed for {registration.email}: {e}")
        
        # Log the failure
        EmailLog.objects.create(
            registration=registration,
            email_type='apology',
            sent_by=None,
            success=False,
            error_message=str(e)
        )
        
        return False

def restore_bulk_rejected_participants():
    """Main function to restore bulk rejected participants"""
    
    print("=== BULK REJECTION RESTORATION TOOL ===")
    
    # Create apology email template
    create_apology_email_template()
    
    # Find bulk rejected participants (rejected_by is None)
    bulk_rejected = EventRegistration.objects.filter(
        approval_status='rejected',
        rejected_by__isnull=True,
        registration_type='participant'  # Only participants
    )
    
    total_count = bulk_rejected.count()
    print(f"Found {total_count} bulk rejected participant registrations")
    
    if total_count == 0:
        print("No bulk rejected participants found!")
        return
    
    # Show breakdown by state
    print("\nBreakdown by state:")
    states = bulk_rejected.values('state').distinct()
    for state_data in states:
        state = state_data['state']
        count = bulk_rejected.filter(state=state).count()
        print(f"  {state}: {count} registrations")
    
    # Confirm action
    proceed = input(f"\nRestore {total_count} registrations to 'pending' and send apology emails? (y/N): ").lower().strip()
    if proceed != 'y':
        print("Operation cancelled.")
        return
    
    # Create CSV file for tracking
    csv_filename = f"restored_registrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    csv_path = os.path.join(os.getcwd(), csv_filename)
    
    # Process registrations
    restored_count = 0
    email_sent_count = 0
    email_failed_count = 0
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'id', 'full_name', 'phone', 'email', 'state', 'city', 
            'registration_date', 'previous_status', 'new_status', 
            'restored_at', 'email_sent', 'email_status'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        print(f"\nProcessing {total_count} registrations...")
        
        for i, registration in enumerate(bulk_rejected, 1):
            try:
                # Store original status
                original_status = registration.approval_status
                
                # Update status to pending
                registration.approval_status = 'pending'
                registration.rejected_by = None
                registration.rejected_at = None
                registration._skip_auto_email = True  # Skip auto email
                registration.save()
                
                restored_count += 1
                
                # Send apology email
                email_success = send_apology_email(registration)
                if email_success:
                    email_sent_count += 1
                    email_status = 'sent'
                else:
                    email_failed_count += 1
                    email_status = 'failed'
                
                # Write to CSV
                writer.writerow({
                    'id': registration.id,
                    'full_name': registration.full_name,
                    'phone': registration.phone,
                    'email': registration.email,
                    'state': registration.state,
                    'city': registration.city,
                    'registration_date': registration.registration_date,
                    'previous_status': original_status,
                    'new_status': registration.approval_status,
                    'restored_at': timezone.now(),
                    'email_sent': email_success,
                    'email_status': email_status
                })
                
                # Progress update
                if i % 50 == 0 or i == total_count:
                    print(f"Processed {i}/{total_count} registrations...")
                
                # Small delay to avoid overwhelming email server
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error processing {registration.full_name} ({registration.phone}): {e}")
                continue
    
    # Final summary
    print(f"\n=== RESTORATION COMPLETE ===")
    print(f"Total processed: {total_count}")
    print(f"Successfully restored: {restored_count}")
    print(f"Apology emails sent: {email_sent_count}")
    print(f"Email failures: {email_failed_count}")
    print(f"Success rate: {(restored_count/total_count*100):.1f}%")
    print(f"Email success rate: {(email_sent_count/total_count*100):.1f}%")
    print(f"CSV file created: {csv_path}")
    
    print(f"\n✅ All bulk rejected participants have been restored to 'pending' status!")
    print(f"📧 Apology emails sent explaining the technical issue.")
    print(f"📊 Complete record saved in: {csv_filename}")

if __name__ == "__main__":
    restore_bulk_rejected_participants()