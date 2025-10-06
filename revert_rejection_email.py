#!/usr/bin/env python
import subprocess
import os

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd='e:/Divy/Projects/GitHub/ycsmp')
        print(f"Command: {command}")
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Exception: {e}")
        return False

print("=== Reverting Rejection Email Commit ===")

# Option 1: Revert the specific commit (creates a new commit that undoes the changes)
print("\n1. Creating revert commit...")
success = run_command('git revert 0116cd7 --no-edit')

if success:
    print("✅ Rejection email commit reverted successfully!")
    print("All changes from commit 0116cd7 have been undone.")
    print("A new revert commit has been created.")
else:
    print("❌ Revert failed. Trying alternative approach...")
    
    # Option 2: Reset specific files to the state before the rejection email commit
    print("\n2. Resetting specific files...")
    files_to_reset = [
        'events/admin.py',
        'events/email_utils.py', 
        'events/models.py',
        'templates/events/emails/registration_rejected.html'
    ]
    
    for file in files_to_reset:
        print(f"Resetting {file}...")
        run_command(f'git checkout e5168da -- {file}')
    
    # Remove the new files that were added
    files_to_remove = [
        'find_unsent_rejection_emails.py',
        'safe_bulk_rejection_emails.py', 
        'test_rejection_email.py'
    ]
    
    for file in files_to_remove:
        if os.path.exists(f'e:/Divy/Projects/GitHub/ycsmp/{file}'):
            print(f"Removing {file}...")
            os.remove(f'e:/Divy/Projects/GitHub/ycsmp/{file}')
    
    print("✅ Files reset to pre-rejection email state!")
    print("You may need to run: python manage.py migrate --fake events 0017")
    print("to undo the EmailLog migration if needed.")

print("\n=== Revert Complete ===")
print("Check git status to see the changes.")