#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')

# Setup Django
django.setup()

from django.contrib.auth.models import User
from events.models import ApprovalUser

def check_ambekar_user():
    print("🔍 Checking Ambekar_mp user configuration...")
    
    # Find user with ambekar in username
    users = User.objects.filter(username__icontains='ambekar')
    print(f"Found {users.count()} users with 'ambekar' in username:")
    
    for user in users:
        print(f"\n👤 User: {user.username} ({user.first_name} {user.last_name})")
        print(f"   Email: {user.email}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Superuser: {user.is_superuser}")
        
        # Check ApprovalUser configuration
        try:
            approval_user = ApprovalUser.objects.get(user=user)
            print(f"\n📋 ApprovalUser Configuration:")
            print(f"   State Code: {approval_user.state_code}")
            print(f"   Is Super Approver: {approval_user.is_super_approver}")
            print(f"   Is State Approver: {approval_user.is_state_approver}")
            print(f"   Is District Approver: {approval_user.is_district_approver}")
            print(f"   Is UpZone Approver: {approval_user.is_upzone_approver}")
            print(f"   Districts: {approval_user.districts}")
            print(f"   UpZone: {approval_user.upzone}")
            print(f"   Allowed Registration Types: {approval_user.allowed_registration_types}")
            
            # Check what this user can approve
            print(f"\n🔐 Approval Capabilities:")
            if approval_user.is_super_approver:
                print("   ✅ Can approve ALL registrations at ALL levels")
            elif approval_user.is_state_approver:
                print(f"   ✅ Can do STATE level approvals for {approval_user.state_code}")
            elif approval_user.is_upzone_approver:
                if approval_user.upzone:
                    print(f"   ✅ Can do UPZONE level approvals for {approval_user.upzone.name}")
                    print(f"   📍 UpZone Districts: {approval_user.upzone.districts}")
                else:
                    print("   ❌ UpZone approver but NO UpZone assigned!")
            elif approval_user.is_district_approver:
                if approval_user.districts:
                    print(f"   ✅ Can do DISTRICT level approvals for: {', '.join(approval_user.districts)}")
                else:
                    print("   ❌ District approver but NO districts assigned!")
            else:
                print("   ❌ NO approval permissions set!")
            
            if approval_user.allowed_registration_types:
                print(f"   📝 Can only approve: {', '.join(approval_user.allowed_registration_types)}")
            else:
                print("   📝 Can approve ALL registration types")
                
        except ApprovalUser.DoesNotExist:
            print(f"\n❌ NO ApprovalUser configuration found for {user.username}")
            print("   This user cannot approve any registrations!")
    
    if not users.exists():
        print("❌ No users found with 'ambekar' in username")
        print("\n🔍 Searching for similar usernames...")
        similar_users = User.objects.filter(username__icontains='amb')
        for user in similar_users:
            print(f"   - {user.username}")

if __name__ == "__main__":
    check_ambekar_user()