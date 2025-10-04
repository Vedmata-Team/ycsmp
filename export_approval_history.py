#!/usr/bin/env python
import os
import django
import csv
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration

def export_approval_history_csv():
    """Export approval history to CSV"""
    
    registrations = EventRegistration.objects.filter(
        registration_type__in=['volunteer', 'organization_representative']
    ).order_by('-registration_date')
    
    filename = f"approval_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        writer.writerow([
            'Name', 'Type', 'Phone', 'City', 'State', 'Current Status',
            'District Approver', 'District Approved At',
            'Upzone Approver', 'Upzone Approved At', 
            'Final Approver', 'Final Approved At',
            'Rejected By', 'Rejected At',
            'Registration Date'
        ])
        
        # Data
        for reg in registrations:
            writer.writerow([
                reg.full_name,
                reg.get_registration_type_display(),
                reg.phone,
                reg.city,
                reg.state,
                reg.approval_status,
                reg.district_approver.username if reg.district_approver else '',
                reg.district_approved_at.strftime('%Y-%m-%d %H:%M:%S') if reg.district_approved_at else '',
                reg.upzone_approver.username if reg.upzone_approver else '',
                reg.upzone_approved_at.strftime('%Y-%m-%d %H:%M:%S') if reg.upzone_approved_at else '',
                reg.final_approver.username if reg.final_approver else '',
                reg.final_approved_at.strftime('%Y-%m-%d %H:%M:%S') if reg.final_approved_at else '',
                getattr(reg, 'rejected_by', None) and reg.rejected_by.username or '',
                getattr(reg, 'rejected_at', None) and reg.rejected_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                reg.registration_date.strftime('%Y-%m-%d %H:%M:%S')
            ])
    
    print(f"✅ Exported {registrations.count()} registrations to {filename}")
    return filename

if __name__ == "__main__":
    export_approval_history_csv()