#!/usr/bin/env python3
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration

# Find Dr Rajesh Amrute (primary user)
primary = EventRegistration.objects.filter(full_name__icontains='Rajesh Amrute').first()

if primary:
    print(f"✅ Primary user: {primary.full_name}")
    print(f"📞 Phone: {primary.phone}")
    print(f"🎂 DOB: {primary.date_of_birth}")
    print(f"🚗 Vehicle: {primary.vehicle_number}")
    print(f"🆔 ID: {primary.id}")
    print(f"\n🔗 Vehicle Pass Preview URL:")
    print(f"http://127.0.0.1:8000/vehicle-pass/preview/{primary.id}/{primary.vehicle_number}/")
else:
    print("❌ Dr Rajesh Amrute not found")