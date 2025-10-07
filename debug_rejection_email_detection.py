#!/usr/bin/env python3
"""
Debug Rejection Email Detection
==============================
Debug why specific rejected users aren't being detected
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration, EmailLog

def debug_specific_user():
    """Debug the specific user mentioned"""
    
    print("🔍 DEBUGGING SPECIFIC USER: नरिंग भयड़िया")
    print("=" * 50)
    
    # Find the user by name and phone
    user = EventRegistration.objects.filter(
        full_name__icontains="नरिंग",
        phone="9343797113"
    ).first()
    
    if not user:
        print("❌ User not found with name containing 'नरिंग' and phone '9343797113'")
        
        # Try broader search
        users_by_phone = EventRegistration.objects.filter(phone="9343797113")
        print(f"Users with phone 9343797113: {users_by_phone.count()}")
        
        for u in users_by_phone:
            print(f"  - {u.full_name} | {u.approval_status} | {u.email}")
        
        return
    
    print(f"✅ Found user: {user.full_name}")
    print(f"📧 Email: {user.email}")
    print(f"📱 Phone: {user.phone}")
    print(f"🏢 Type: {user.get_registration_type_display()}")
    print(f"📍 Location: {user.city}, {user.state}")
    print(f"🆔 ID: {user.id}")
    print(f"📊 Approval Status: {user.approval_status}")
    print(f"📧 Email Sent Flag: {user.email_sent}")
    
    # Check rejection details
    if hasattr(user, 'rejected_by') and user.rejected_by:
        print(f"👤 Rejected by: {user.rejected_by.get_full_name() or user.rejected_by.username}")
    
    if hasattr(user, 'rejected_at') and user.rejected_at:
        print(f"📅 Rejected at: {user.rejected_at.strftime('%d/%m/%Y %H:%M:%S')}")
    
    if hasattr(user, 'rejection_reason') and user.rejection_reason:
        print(f"📝 Reason: {user.rejection_reason}")
    
    # Check EmailLog entries
    print(f"\n📋 EMAIL LOG ENTRIES:")
    email_logs = EmailLog.objects.filter(registration=user).order_by('-sent_at')
    
    if email_logs.exists():
        for log in email_logs:
            status = "✅ Success" if log.success else "❌ Failed"
            print(f"  - {log.email_type} | {status} | {log.sent_at.strftime('%d/%m/%Y %H:%M:%S')}")
            if log.error_message:
                print(f"    Error: {log.error_message}")
    else:
        print("  No email logs found")
    
    # Check if user needs rejection email
    has_rejection_email = EmailLog.objects.filter(
        registration=user,
        email_type='rejection',
        success=True
    ).exists()
    
    print(f"\n🔍 DETECTION ANALYSIS:")
    print(f"Has successful rejection email log: {has_rejection_email}")
    print(f"Email sent flag: {user.email_sent}")
    print(f"Approval status: {user.approval_status}")
    
    needs_email = (user.approval_status == 'rejected' and 
                   not has_rejection_email and 
                   not user.email_sent)
    
    print(f"Needs rejection email: {needs_email}")
    
    return user

def debug_all_rejected_users():
    """Debug all rejected users and their email status"""
    
    print("\n🔍 DEBUGGING ALL REJECTED USERS")
    print("=" * 50)
    
    rejected_users = EventRegistration.objects.filter(approval_status='rejected')
    total = rejected_users.count()
    
    print(f"Total rejected users: {total}")
    
    # Categorize users
    with_email_log = 0
    with_email_flag = 0
    with_both = 0
    with_neither = 0
    
    users_needing_emails = []
    
    for user in rejected_users:
        has_rejection_log = EmailLog.objects.filter(
            registration=user,
            email_type='rejection',
            success=True
        ).exists()
        
        has_email_flag = user.email_sent
        
        if has_rejection_log and has_email_flag:
            with_both += 1
        elif has_rejection_log:
            with_email_log += 1
        elif has_email_flag:
            with_email_flag += 1
        else:
            with_neither += 1
            users_needing_emails.append(user)
    
    print(f"\n📊 EMAIL STATUS BREAKDOWN:")
    print(f"With both email log and flag: {with_both}")
    print(f"With email log only: {with_email_log}")
    print(f"With email flag only: {with_email_flag}")
    print(f"With neither (need emails): {with_neither}")
    
    if users_needing_emails:
        print(f"\n📋 USERS NEEDING EMAILS (first 10):")
        for i, user in enumerate(users_needing_emails[:10], 1):
            print(f"{i:2d}. {user.full_name} ({user.email}) - ID: {user.id}")
    
    return users_needing_emails

def main():
    """Main debug function"""
    
    print("🐛 REJECTION EMAIL DETECTION DEBUG")
    print("=" * 60)
    
    # Debug specific user
    specific_user = debug_specific_user()
    
    # Debug all rejected users
    users_needing_emails = debug_all_rejected_users()
    
    print(f"\n🎯 SUMMARY:")
    print(f"Specific user found: {'Yes' if specific_user else 'No'}")
    print(f"Total users needing emails: {len(users_needing_emails)}")
    
    if specific_user and specific_user in users_needing_emails:
        print("✅ Specific user IS in the list of users needing emails")
    elif specific_user:
        print("⚠️  Specific user is NOT in the list of users needing emails")
        print("This means they already have email_sent=True or successful rejection email log")

if __name__ == "__main__":
    main()