#!/usr/bin/env python
import os

def remove_rejection_email_features():
    print("=== Safely Removing Rejection Email Features ===")
    
    # 1. Remove the standalone rejection email files (safe to delete)
    files_to_remove = [
        'find_unsent_rejection_emails.py',
        'safe_bulk_rejection_emails.py', 
        'test_rejection_email.py'
    ]
    
    for file in files_to_remove:
        file_path = f'e:/Divy/Projects/GitHub/ycsmp/{file}'
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ Removed {file}")
        else:
            print(f"⏭️ {file} not found")
    
    print("\n=== Manual Steps Required ===")
    print("The following need to be manually removed from existing files:")
    print("\n1. In events/admin.py:")
    print("   - Remove 'send_email_to_rejected' action from EventRegistrationAdmin")
    print("   - Remove the send_email_to_rejected method")
    print("   - Remove EmailLog import and admin registration")
    
    print("\n2. In events/models.py:")
    print("   - Remove EmailLog model class")
    print("   - Remove EmailLog import in admin.py")
    
    print("\n3. In events/email_utils.py:")
    print("   - Remove EmailLog logging code from send_registration_approval_email")
    print("   - Keep the basic email sending functionality")
    
    print("\n4. Database migration:")
    print("   - Run: python manage.py migrate events 0017 --fake")
    print("   - Delete: events/migrations/0018_emaillog.py")
    
    print("\n✅ Safe removal completed!")
    print("This approach preserves all commits after 'Rejection email' commit.")

if __name__ == '__main__':
    remove_rejection_email_features()