#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration

def detect_mp_districts():
    """Detect all MP districts from registration data"""
    
    # Get all unique cities from MP registrations
    mp_districts = EventRegistration.objects.filter(
        models.Q(state__icontains='madhya pradesh') |
        models.Q(state__iexact='MP') |
        models.Q(state__icontains='mp')
    ).values_list('city', flat=True).distinct().order_by('city')
    
    mp_districts = [district for district in mp_districts if district and district.strip()]
    
    print(f"Found {len(mp_districts)} districts in MP:")
    print("=" * 50)
    
    for i, district in enumerate(mp_districts, 1):
        count = EventRegistration.objects.filter(
            city=district,
            state__icontains='madhya pradesh'
        ).count()
        print(f"{i:2d}. {district} ({count} registrations)")
    
    print("=" * 50)
    print(f"Total MP Districts: {len(mp_districts)}")
    
    # Export as list for easy copying
    print("\nDistricts as Python list:")
    print(mp_districts)
    
    return mp_districts

if __name__ == "__main__":
    from django.db import models
    detect_mp_districts()