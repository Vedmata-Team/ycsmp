#!/usr/bin/env python3
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration

# Find approved user with vehicle
user = EventRegistration.objects.filter(
    approval_status='approved',
    vehicle_number__isnull=False
).exclude(vehicle_number='').first()

if user:
    print(f"✅ Found user: {user.full_name}")
    print(f"📞 Phone: {user.phone}")
    print(f"🎂 DOB: {user.date_of_birth}")
    print(f"🚗 Vehicle: {user.vehicle_number}")
    print(f"🆔 ID: {user.id}")
    print(f"\n🔗 Vehicle Pass Preview URL:")
    print(f"https://ycsmp.in/vehicle-pass/preview/{user.id}/{user.vehicle_number}/")
    print(f"\n🔗 Profile URL:")
    print(f"https://ycsmp.in{user.get_profile_url()}")
else:
    print("❌ No approved users with vehicles found")