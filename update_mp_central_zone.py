#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import UpZone, EventRegistration
from django.db import models

def update_mp_central_zone():
    """Update MP Central Zone to include all MP districts"""
    
    # Get all unique MP districts from registration data
    mp_districts = EventRegistration.objects.filter(
        models.Q(state__icontains='madhya pradesh') |
        models.Q(state__iexact='MP')
    ).values_list('city', flat=True).distinct().order_by('city')
    
    mp_districts = [d for d in mp_districts if d and d.strip()]
    
    try:
        # Get MP Central Zone (ID 13)
        mp_central_zone = UpZone.objects.get(id=13)
        
        # Update with all MP districts
        mp_central_zone.districts = mp_districts
        mp_central_zone.save()
        
        print(f"✅ Updated MP Central Zone with {len(mp_districts)} districts:")
        print("=" * 60)
        for i, district in enumerate(mp_districts, 1):
            print(f"{i:2d}. {district}")
        
        print("=" * 60)
        print(f"Total districts: {len(mp_districts)}")
        
        return True
        
    except UpZone.DoesNotExist:
        print("❌ MP Central Zone (ID 13) not found!")
        return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    update_mp_central_zone()