#!/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration
from django.db import connection

def check_rejection_source():
    """Check possible sources of bulk rejection"""
    
    # Check registrations with similar pattern (rejected but no rejected_by)
    bulk_rejected = EventRegistration.objects.filter(
        approval_status='rejected',
        rejected_by__isnull=True
    )
    
    print(f"=== BULK REJECTED REGISTRATIONS (No rejected_by) ===")
    print(f"Total count: {bulk_rejected.count()}")
    
    # Group by state to see pattern
    states = bulk_rejected.values('state').distinct()
    for state_data in states:
        state = state_data['state']
        count = bulk_rejected.filter(state=state).count()
        print(f"{state}: {count} registrations")
    
    # Check if there's a pattern in registration dates
    print(f"\n=== REGISTRATION DATE PATTERN ===")
    reg_dates = bulk_rejected.values('registration_date__date').distinct().order_by('registration_date__date')
    for date_data in reg_dates[:10]:  # Show first 10 dates
        date = date_data['registration_date__date']
        count = bulk_rejected.filter(registration_date__date=date).count()
        print(f"{date}: {count} rejections")
    
    # Check specific registration details
    reg = EventRegistration.objects.get(phone="9610290010")
    print(f"\n=== SPECIFIC REGISTRATION DETAILS ===")
    print(f"Registration Date: {reg.registration_date}")
    print(f"State: {reg.state}")
    print(f"City: {reg.city}")
    print(f"Documents uploaded:")
    print(f"  - Aadhar Full: {bool(reg.aadhar_full)}")
    print(f"  - Aadhar Front: {bool(reg.aadhar_front)}")
    print(f"  - Aadhar Back: {bool(reg.aadhar_back)}")
    print(f"  - Passport Photo: {bool(reg.passport_photo)}")
    
    # Check if rejection might be due to missing documents
    missing_docs = []
    if not reg.passport_photo:
        missing_docs.append("Passport Photo")
    if not reg.aadhar_full and not (reg.aadhar_front and reg.aadhar_back):
        missing_docs.append("Aadhar Card")
    
    if missing_docs:
        print(f"Missing documents: {', '.join(missing_docs)}")
    else:
        print("All required documents present")
    
    # Check for similar registrations from same state that were also rejected
    similar_rejected = EventRegistration.objects.filter(
        state=reg.state,
        approval_status='rejected',
        rejected_by__isnull=True
    ).exclude(id=reg.id)
    
    print(f"\n=== SIMILAR REJECTIONS FROM {reg.state} ===")
    print(f"Count: {similar_rejected.count()}")
    
    if similar_rejected.exists():
        print("Sample rejected registrations from same state:")
        for similar in similar_rejected[:5]:
            print(f"- {similar.full_name} ({similar.phone}) from {similar.city}")

if __name__ == "__main__":
    check_rejection_source()