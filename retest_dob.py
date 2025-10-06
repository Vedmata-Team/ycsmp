#!/usr/bin/env python3
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration

# Get Dr Rajesh Amrute for testing
user = EventRegistration.objects.get(id=934)

print("🧪 RETEST DOB VALIDATION")
print("=" * 40)
print(f"👤 User: {user.full_name}")
print(f"🎂 DOB: {user.date_of_birth}")
print(f"🚗 Vehicle: {user.vehicle_number}")
print(f"🆔 ID: {user.id}")
print()
print("🔗 Test URL:")
print(f"http://127.0.0.1:8000/vehicle-pass/preview/{user.id}/{user.vehicle_number}/")
print()
print("✅ Expected DOB input: 1989-06-25")
print("❌ Wrong DOB test: 1990-01-01")
print()
print("📋 What to check:")
print("1. Console should show: 🎯 IMMEDIATE - USER_DOB set to: 1989-06-25")
print("2. Constructor should show: 🔧 this.userDOB set to: 1989-06-25")
print("3. Validation should PASS with: 1989-06-25")
print("4. Validation should FAIL with: 1990-01-01")