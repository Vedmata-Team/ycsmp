#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration, EmailLog
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType

def investigate_rejection(phone):
    """Comprehensive investigation of who rejected a registration"""
    try:
        registration = EventRegistration.objects.get(phone=phone)
        
        print(f"=== REJECTION INVESTIGATION ===")
        print(f"Name: {registration.full_name}")
        print(f"Phone: {registration.phone}")
        print(f"Registration ID: {registration.id}")
        print(f"Status: {registration.approval_status}")
        print(f"Rejected At: {registration.rejected_at}")
        print(f"Rejected By: {registration.rejected_by}")
        
        # 1. Check Django Admin Log Entries
        print(f"\n=== DJANGO ADMIN LOGS ===")
        content_type = ContentType.objects.get_for_model(EventRegistration)
        admin_logs = LogEntry.objects.filter(
            content_type=content_type,
            object_id=str(registration.id)
        ).order_by('-action_time')
        
        for log in admin_logs:
            print(f"Action: {log.get_action_flag_display()}")
            print(f"User: {log.user.username} ({log.user.get_full_name()})")
            print(f"Time: {log.action_time}")
            print(f"Message: {log.change_message}")
            print(f"---")
        
        # 2. Check Email Logs for rejection emails
        print(f"\n=== EMAIL LOGS ===")
        email_logs = EmailLog.objects.filter(
            registration=registration,
            email_type='rejection'
        ).order_by('-sent_at')
        
        for email_log in email_logs:
            print(f"Email Type: {email_log.email_type}")
            print(f"Sent By: {email_log.sent_by}")
            print(f"Sent At: {email_log.sent_at}")
            print(f"Success: {email_log.success}")
            print(f"---")
        
        # 3. Check for bulk rejection activities around the time
        if registration.rejected_at:
            time_window = timedelta(hours=2)
            start_time = registration.rejected_at - time_window
            end_time = registration.rejected_at + time_window
            
            print(f"\n=== BULK REJECTIONS AROUND SAME TIME ===")
            print(f"Time window: {start_time} to {end_time}")
            
            similar_rejections = EventRegistration.objects.filter(
                approval_status='rejected',
                rejected_at__range=[start_time, end_time]
            ).exclude(id=registration.id)
            
            print(f"Found {similar_rejections.count()} other rejections in same time window:")
            for reg in similar_rejections[:5]:  # Show first 5
                print(f"- {reg.full_name} ({reg.phone}) - Rejected by: {reg.rejected_by}")
        
        # 4. Check admin logs for bulk actions around that time
        print(f"\n=== ADMIN BULK ACTIONS ===")
        if registration.rejected_at:
            bulk_logs = LogEntry.objects.filter(
                content_type=content_type,
                action_time__range=[start_time, end_time],
                change_message__icontains='rejected'
            ).order_by('-action_time')
            
            for log in bulk_logs[:10]:  # Show first 10
                print(f"User: {log.user.username}")
                print(f"Time: {log.action_time}")
                print(f"Message: {log.change_message}")
                print(f"---")
        
        # 5. Check for users who have rejection permissions for this state/district
        print(f"\n=== USERS WITH REJECTION PERMISSIONS ===")
        from events.models import ApprovalUser
        
        # Find approval users for this registration's location
        state_code = registration.state_code
        city = registration.city
        
        potential_approvers = ApprovalUser.objects.filter(
            state_code=state_code
        )
        
        if state_code == 'MP':
            # For MP, also check district-specific approvers
            district_approvers = ApprovalUser.objects.filter(
                state_code='MP',
                is_district_approver=True,
                districts__contains=[city]
            )
            potential_approvers = potential_approvers.union(district_approvers)
        
        print(f"Users who can approve/reject registrations from {city}, {registration.state}:")
        for approver in potential_approvers:
            print(f"- {approver.user.username} ({approver.user.get_full_name()})")
            print(f"  Roles: District={approver.is_district_approver}, State={approver.is_state_approver}, Super={approver.is_super_approver}")
        
        # 6. Check recent login activity of potential approvers
        print(f"\n=== RECENT ACTIVITY OF POTENTIAL APPROVERS ===")
        if registration.rejected_at:
            for approver in potential_approvers:
                user = approver.user
                print(f"User: {user.username}")
                print(f"Last Login: {user.last_login}")
                
                # Check their recent admin actions
                recent_actions = LogEntry.objects.filter(
                    user=user,
                    action_time__gte=registration.rejected_at - timedelta(days=1),
                    action_time__lte=registration.rejected_at + timedelta(hours=1)
                ).order_by('-action_time')[:5]
                
                if recent_actions:
                    print(f"Recent actions around rejection time:")
                    for action in recent_actions:
                        print(f"  - {action.action_time}: {action.change_message}")
                print(f"---")
        
    except EventRegistration.DoesNotExist:
        print(f"No registration found with phone number: {phone}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    phone = "9610290010"
    investigate_rejection(phone)