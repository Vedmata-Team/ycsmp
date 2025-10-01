#!/usr/bin/env python3
"""
Test profile URL generation
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration

def test_profile_urls():
    """Test profile URL generation for first 5 registrations"""
    print("🔗 Testing Profile URL Generation")
    print("=" * 50)
    
    registrations = EventRegistration.objects.select_related('event')[:5]
    
    for reg in registrations:
        profile_url = reg.get_profile_url()
        full_url = f"http://127.0.0.1:8000{profile_url}"
        
        print(f"\n👤 {reg.full_name}")
        print(f"   Type: {reg.get_registration_type_display()}")
        print(f"   Status: {reg.get_approval_status_display()}")
        print(f"   Profile URL: {full_url}")
    
    print(f"\n✅ Generated {len(registrations)} profile URLs")
    print("\nTo test:")
    print("1. Start Django server: python manage.py runserver")
    print("2. Visit any of the URLs above")

if __name__ == "__main__":
    test_profile_urls()