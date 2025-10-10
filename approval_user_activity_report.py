#!/usr/bin/env python
"""
Comprehensive Approval User Activity Report
Exports detailed statistics of approval users' activities
"""
import os
import sys
import django
import csv
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration, ApprovalUser
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

def calculate_active_hours(user):
    """Calculate total active hours for a user based on admin log entries"""
    try:
        # Get all admin log entries for this user
        logs = LogEntry.objects.filter(user=user).order_by('action_time')
        
        if not logs.exists():
            return 0.0
        
        total_hours = 0.0
        session_start = None
        last_activity = None
        
        for log in logs:
            if session_start is None:
                session_start = log.action_time
                last_activity = log.action_time
            else:
                # If gap between activities is more than 30 minutes, consider it a new session
                time_gap = (log.action_time - last_activity).total_seconds() / 60  # minutes
                
                if time_gap > 30:  # 30 minutes gap = new session
                    # Add previous session duration
                    session_duration = (last_activity - session_start).total_seconds() / 3600  # hours
                    total_hours += max(session_duration, 0.1)  # Minimum 6 minutes per session
                    
                    # Start new session
                    session_start = log.action_time
                
                last_activity = log.action_time
        
        # Add final session
        if session_start and last_activity:
            session_duration = (last_activity - session_start).total_seconds() / 3600
            total_hours += max(session_duration, 0.1)
        
        return round(total_hours, 2)
        
    except Exception as e:
        print(f"Error calculating active hours for {user.username}: {e}")
        return 0.0

def generate_approval_user_report():
    """Generate comprehensive approval user activity report"""
    
    print("=== APPROVAL USER ACTIVITY REPORT ===")
    
    # Get all approval users
    approval_users = ApprovalUser.objects.select_related('user').all()
    
    # Prepare data structure
    user_stats = []
    
    for approval_user in approval_users:
        user = approval_user.user
        
        print(f"Processing: {user.username}...")
        
        # Get all registrations handled by this user
        district_approvals = EventRegistration.objects.filter(district_approver=user)
        upzone_approvals = EventRegistration.objects.filter(upzone_approver=user)
        final_approvals = EventRegistration.objects.filter(final_approver=user)
        rejections = EventRegistration.objects.filter(rejected_by=user)
        
        # Count by registration type for approvals
        approval_stats = {
            'district_participant': district_approvals.filter(registration_type='participant').count(),
            'district_volunteer': district_approvals.filter(registration_type='volunteer').count(),
            'district_organization': district_approvals.filter(registration_type='organization_representative').count(),
            'upzone_participant': upzone_approvals.filter(registration_type='participant').count(),
            'upzone_volunteer': upzone_approvals.filter(registration_type='volunteer').count(),
            'upzone_organization': upzone_approvals.filter(registration_type='organization_representative').count(),
            'final_participant': final_approvals.filter(registration_type='participant').count(),
            'final_volunteer': final_approvals.filter(registration_type='volunteer').count(),
            'final_organization': final_approvals.filter(registration_type='organization_representative').count(),
        }
        
        # Count by registration type for rejections
        rejection_stats = {
            'rejected_participant': rejections.filter(registration_type='participant').count(),
            'rejected_volunteer': rejections.filter(registration_type='volunteer').count(),
            'rejected_organization': rejections.filter(registration_type='organization_representative').count(),
        }
        
        # Calculate totals
        total_district_approvals = district_approvals.count()
        total_upzone_approvals = upzone_approvals.count()
        total_final_approvals = final_approvals.count()
        total_approvals = total_district_approvals + total_upzone_approvals + total_final_approvals
        total_rejections = rejections.count()
        total_activity = total_approvals + total_rejections
        
        # Calculate active hours
        active_hours = calculate_active_hours(user)
        
        # Compile user statistics
        user_data = {
            'username': user.username,
            'full_name': user.get_full_name() or 'No Name',
            'email': user.email,
            'is_active': user.is_active,
            'last_login': user.last_login,
            'date_joined': user.date_joined,
            
            # Approval User Details
            'state_code': approval_user.state_code,
            'is_super_approver': approval_user.is_super_approver,
            'is_state_approver': approval_user.is_state_approver,
            'is_district_approver': approval_user.is_district_approver,
            'is_upzone_approver': approval_user.is_upzone_approver,
            'districts': ', '.join(approval_user.districts) if approval_user.districts else '',
            'upzone': approval_user.upzone.name if approval_user.upzone else '',
            
            # District Level Approvals
            'district_approvals_total': total_district_approvals,
            'district_participant': approval_stats['district_participant'],
            'district_volunteer': approval_stats['district_volunteer'],
            'district_organization': approval_stats['district_organization'],
            
            # UpZone Level Approvals
            'upzone_approvals_total': total_upzone_approvals,
            'upzone_participant': approval_stats['upzone_participant'],
            'upzone_volunteer': approval_stats['upzone_volunteer'],
            'upzone_organization': approval_stats['upzone_organization'],
            
            # Final Level Approvals
            'final_approvals_total': total_final_approvals,
            'final_participant': approval_stats['final_participant'],
            'final_volunteer': approval_stats['final_volunteer'],
            'final_organization': approval_stats['final_organization'],
            
            # Total Approvals
            'total_approvals': total_approvals,
            
            # Rejections
            'total_rejections': total_rejections,
            'rejected_participant': rejection_stats['rejected_participant'],
            'rejected_volunteer': rejection_stats['rejected_volunteer'],
            'rejected_organization': rejection_stats['rejected_organization'],
            
            # Activity Summary
            'total_activity_count': total_activity,
            'active_hours': active_hours,
            
            # Performance Metrics
            'approval_rate': round((total_approvals / total_activity * 100), 2) if total_activity > 0 else 0,
            'rejection_rate': round((total_rejections / total_activity * 100), 2) if total_activity > 0 else 0,
            'activity_per_hour': round((total_activity / active_hours), 2) if active_hours > 0 else 0,
        }
        
        user_stats.append(user_data)
    
    # Sort by total activity (descending)
    user_stats.sort(key=lambda x: x['total_activity_count'], reverse=True)
    
    # Display summary
    print(f"\n=== APPROVAL USER SUMMARY ===")
    print(f"{'Username':<20} {'Total Activity':<15} {'Approvals':<10} {'Rejections':<10} {'Active Hours':<12} {'Rate':<10}")
    print("-" * 85)
    
    for user_data in user_stats:
        print(f"{user_data['username']:<20} {user_data['total_activity_count']:<15} {user_data['total_approvals']:<10} {user_data['total_rejections']:<10} {user_data['active_hours']:<12} {user_data['approval_rate']:.1f}%")
    
    # Create CSV report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"approval_user_activity_report_{timestamp}.csv"
    csv_path = os.path.join(os.getcwd(), csv_filename)
    
    fieldnames = [
        'username', 'full_name', 'email', 'is_active', 'last_login', 'date_joined',
        'state_code', 'is_super_approver', 'is_state_approver', 'is_district_approver', 'is_upzone_approver',
        'districts', 'upzone',
        'district_approvals_total', 'district_participant', 'district_volunteer', 'district_organization',
        'upzone_approvals_total', 'upzone_participant', 'upzone_volunteer', 'upzone_organization',
        'final_approvals_total', 'final_participant', 'final_volunteer', 'final_organization',
        'total_approvals',
        'total_rejections', 'rejected_participant', 'rejected_volunteer', 'rejected_organization',
        'total_activity_count', 'active_hours',
        'approval_rate', 'rejection_rate', 'activity_per_hour'
    ]
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(user_stats)
    
    # Generate summary statistics
    total_users = len(user_stats)
    active_users = len([u for u in user_stats if u['total_activity_count'] > 0])
    total_system_approvals = sum(u['total_approvals'] for u in user_stats)
    total_system_rejections = sum(u['total_rejections'] for u in user_stats)
    total_system_activity = sum(u['total_activity_count'] for u in user_stats)
    total_system_hours = sum(u['active_hours'] for u in user_stats)
    
    print(f"\n=== SYSTEM STATISTICS ===")
    print(f"Total Approval Users: {total_users}")
    print(f"Active Users (with activity): {active_users}")
    print(f"Inactive Users: {total_users - active_users}")
    print(f"Total System Approvals: {total_system_approvals}")
    print(f"Total System Rejections: {total_system_rejections}")
    print(f"Total System Activity: {total_system_activity}")
    print(f"Total Active Hours: {total_system_hours:.2f}")
    print(f"Average Activity per User: {total_system_activity / total_users:.2f}")
    print(f"Average Hours per User: {total_system_hours / total_users:.2f}")
    print(f"System Approval Rate: {(total_system_approvals / total_system_activity * 100):.2f}%" if total_system_activity > 0 else "0%")
    
    # Top performers
    print(f"\n=== TOP PERFORMERS ===")
    print("By Total Activity:")
    for i, user_data in enumerate(user_stats[:5], 1):
        print(f"{i}. {user_data['username']} - {user_data['total_activity_count']} activities")
    
    print("\nBy Active Hours:")
    top_by_hours = sorted(user_stats, key=lambda x: x['active_hours'], reverse=True)[:5]
    for i, user_data in enumerate(top_by_hours, 1):
        print(f"{i}. {user_data['username']} - {user_data['active_hours']} hours")
    
    print(f"\n✅ Report generated: {csv_filename}")
    print(f"📊 Total records: {len(user_stats)}")

if __name__ == "__main__":
    generate_approval_user_report()