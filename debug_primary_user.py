#!/usr/bin/env python3
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration
from vehicle_pass.views import get_primary_vehicle_user

# Check Dr Rajesh Amrute
user = EventRegistration.objects.get(id=934)
print(f"User: {user.full_name}")
print(f"Vehicle: {user.vehicle_number}")

# Check primary user
primary_user = get_primary_vehicle_user(user.vehicle_number)
print(f"Primary user: {primary_user.full_name if primary_user else 'None'}")
print(f"Primary user ID: {primary_user.id if primary_user else 'None'}")
print(f"Current user ID: {user.id}")
print(f"Is primary: {not primary_user or primary_user.id == user.id}")

# Check all users with same vehicle
all_users = EventRegistration.objects.filter(
    vehicle_number=user.vehicle_number,
    approval_status__in=['district_approved', 'upzone_approved', 'approved']
)
print(f"\nAll users with vehicle {user.vehicle_number}:")
for u in all_users:
    print(f"- {u.full_name} (ID: {u.id}, Type: {u.registration_type})")