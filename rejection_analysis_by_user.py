#!/usr/bin/env python
"""
Analyze rejections by user to find who rejected how many registrations
"""
import os
import sys
import django
import csv
from datetime import datetime
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration
from django.contrib.auth.models import User
from django.db.models import Count, Q

def analyze_rejections_by_user():
    """Analyze all rejections by user including unknown rejections"""
    
    print("=== REJECTION ANALYSIS BY USER ===")
    
    # Get all rejected registrations
    all_rejected = EventRegistration.objects.filter(approval_status='rejected')
    total_rejected = all_rejected.count()
    
    print(f"Total rejected registrations: {total_rejected}")
    
    # Group by rejected_by user
    rejection_stats = defaultdict(lambda: {
        'count': 0,
        'participants': 0,
        'volunteers': 0,
        'organization_reps': 0,
        'states': set(),
        'registrations': []
    })
    
    # Analyze each rejection
    for reg in all_rejected:
        if reg.rejected_by:
            user_key = f"{reg.rejected_by.username} ({reg.rejected_by.get_full_name() or 'No Full Name'})"
        else:
            user_key = "Unknown/System (सिस्टम)"
        
        # Update stats
        rejection_stats[user_key]['count'] += 1
        rejection_stats[user_key]['states'].add(reg.state)
        
        # Count by registration type
        if reg.registration_type == 'participant':
            rejection_stats[user_key]['participants'] += 1
        elif reg.registration_type == 'volunteer':
            rejection_stats[user_key]['volunteers'] += 1
        elif reg.registration_type == 'organization_representative':
            rejection_stats[user_key]['organization_reps'] += 1
        
        # Store registration details for CSV
        rejection_stats[user_key]['registrations'].append({
            'id': reg.id,
            'name': reg.full_name,
            'phone': reg.phone,
            'email': reg.email,
            'state': reg.state,
            'city': reg.city,
            'registration_type': reg.registration_type,
            'registration_date': reg.registration_date,
            'rejected_at': reg.rejected_at,
        })
    
    # Display summary
    print(f"\n=== REJECTION SUMMARY BY USER ===")
    print(f"{'User':<40} {'Total':<8} {'Participants':<12} {'Volunteers':<10} {'Org Reps':<8} {'States':<15}")
    print("-" * 95)
    
    # Sort by rejection count (descending)
    sorted_users = sorted(rejection_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    
    for user, stats in sorted_users:
        states_str = ', '.join(list(stats['states'])[:3])  # Show first 3 states
        if len(stats['states']) > 3:
            states_str += f" (+{len(stats['states'])-3} more)"
        
        print(f"{user:<40} {stats['count']:<8} {stats['participants']:<12} {stats['volunteers']:<10} {stats['organization_reps']:<8} {states_str:<15}")
    
    # Create detailed CSV report
    csv_filename = f"rejection_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    csv_path = os.path.join(os.getcwd(), csv_filename)
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'rejected_by_user', 'registration_id', 'full_name', 'phone', 'email', 
            'state', 'city', 'registration_type', 'registration_date', 'rejected_at'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for user, stats in sorted_users:
            for reg_data in stats['registrations']:
                writer.writerow({
                    'rejected_by_user': user,
                    'registration_id': reg_data['id'],
                    'full_name': reg_data['name'],
                    'phone': reg_data['phone'],
                    'email': reg_data['email'],
                    'state': reg_data['state'],
                    'city': reg_data['city'],
                    'registration_type': reg_data['registration_type'],
                    'registration_date': reg_data['registration_date'],
                    'rejected_at': reg_data['rejected_at'],
                })
    
    # Show unknown/system rejections in detail
    unknown_stats = rejection_stats.get("Unknown/System (सिस्टम)", None)
    if unknown_stats:
        print(f"\n=== UNKNOWN/SYSTEM REJECTIONS BREAKDOWN ===")
        print(f"Total unknown rejections: {unknown_stats['count']}")
        print(f"Participants: {unknown_stats['participants']}")
        print(f"Volunteers: {unknown_stats['volunteers']}")
        print(f"Organization Representatives: {unknown_stats['organization_reps']}")
        print(f"States affected: {', '.join(unknown_stats['states'])}")
        
        # Show sample unknown rejections
        print(f"\nSample unknown rejections:")
        for i, reg in enumerate(unknown_stats['registrations'][:10]):  # Show first 10
            print(f"{i+1}. {reg['name']} ({reg['phone']}) - {reg['state']}, {reg['city']}")
    
    # Check for potential bulk rejection patterns
    print(f"\n=== BULK REJECTION PATTERN ANALYSIS ===")
    
    # Group by rejection date (if available)
    rejection_dates = defaultdict(int)
    for user, stats in rejection_stats.items():
        for reg in stats['registrations']:
            if reg['rejected_at']:
                date_key = reg['rejected_at'].date()
                rejection_dates[date_key] += 1
    
    if rejection_dates:
        print("Rejections by date:")
        sorted_dates = sorted(rejection_dates.items(), key=lambda x: x[1], reverse=True)
        for date, count in sorted_dates[:10]:  # Show top 10 dates
            print(f"  {date}: {count} rejections")
    else:
        print("No rejection dates available (all rejected_at fields are None)")
    
    # Summary statistics
    print(f"\n=== FINAL STATISTICS ===")
    print(f"Total rejected registrations: {total_rejected}")
    print(f"Number of different rejectors: {len(rejection_stats)}")
    print(f"Unknown/System rejections: {unknown_stats['count'] if unknown_stats else 0}")
    print(f"Known user rejections: {total_rejected - (unknown_stats['count'] if unknown_stats else 0)}")
    print(f"Detailed CSV report: {csv_filename}")
    
    # Show users with rejection permissions
    print(f"\n=== USERS WITH REJECTION PERMISSIONS ===")
    from events.models import ApprovalUser
    
    approval_users = ApprovalUser.objects.select_related('user').all()
    print(f"Total approval users in system: {approval_users.count()}")
    
    for approval_user in approval_users:
        user = approval_user.user
        rejected_count = EventRegistration.objects.filter(rejected_by=user).count()
        print(f"- {user.username} ({user.get_full_name() or 'No Name'}): {rejected_count} rejections")
        print(f"  Roles: District={approval_user.is_district_approver}, State={approval_user.is_state_approver}, Super={approval_user.is_super_approver}")

if __name__ == "__main__":
    analyze_rejections_by_user()