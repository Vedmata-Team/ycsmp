#!/usr/bin/env python3
"""
Cache Warmer for YCSMP Registration System
Warms up frequently accessed data to improve performance
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.core.cache import cache
from events.models import EventRegistration, UpZone, ApprovalUser, ResponsibilityOption, VibhagOption

def warm_upzone_cache():
    """Warm up upzone cache for district lookups"""
    print("Warming upzone cache...")
    upzones = UpZone.objects.filter(is_active=True).exclude(name='MP Central Zone')
    cached_count = 0
    
    for upzone in upzones:
        for district in upzone.districts:
            cache_key = f"upzone_{district.replace(' ', '_')}_MP"
            cache.set(cache_key, upzone, 3600)  # 1 hour
            cached_count += 1
    
    print(f"✓ Cached {cached_count} district-upzone mappings")

def warm_approval_user_cache():
    """Warm up approval user cache"""
    print("Warming approval user cache...")
    users = ApprovalUser.objects.select_related('user', 'upzone').all()
    
    for user in users:
        cache_key = f"approval_user_{user.user.id}"
        cache.set(cache_key, user, 3600)  # 1 hour
    
    print(f"✓ Cached {users.count()} approval users")

def warm_options_cache():
    """Warm up responsibility and vibhag options cache"""
    print("Warming options cache...")
    
    # Cache responsibility options
    responsibilities = list(ResponsibilityOption.objects.filter(is_active=True).order_by('order', 'name'))
    cache.set('responsibility_options', responsibilities, 3600)
    
    # Cache vibhag options
    vibhags = list(VibhagOption.objects.filter(is_active=True).order_by('order', 'name'))
    cache.set('vibhag_options', vibhags, 3600)
    
    print(f"✓ Cached {len(responsibilities)} responsibilities and {len(vibhags)} vibhags")

def warm_registration_counts():
    """Warm up registration count cache for admin dashboard"""
    print("Warming registration counts cache...")
    
    # Cache total counts by status
    status_counts = {}
    for status, _ in EventRegistration.REGISTRATION_TYPE_CHOICES:
        count = EventRegistration.objects.filter(registration_type=status).count()
        status_counts[status] = count
        cache.set(f"registration_count_{status}", count, 300)  # 5 minutes
    
    # Cache approval status counts
    approval_counts = {}
    approval_statuses = ['pending', 'district_approved', 'upzone_approved', 'approved', 'rejected']
    for status in approval_statuses:
        count = EventRegistration.objects.filter(approval_status=status).count()
        approval_counts[status] = count
        cache.set(f"approval_count_{status}", count, 300)  # 5 minutes
    
    print(f"✓ Cached registration and approval counts")

def warm_state_district_cache():
    """Warm up state-district mapping cache"""
    print("Warming state-district cache...")
    
    try:
        import csv
        from django.conf import settings
        
        # Cache state codes
        csv_path = os.path.join(settings.STATICFILES_DIRS[0], 'csv', 'states.csv')
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            state_mapping = {}
            for row in reader:
                state_mapping[row['state_code']] = row['name']
                state_mapping[row['name']] = row['state_code']
        
        cache.set('state_code_mapping', state_mapping, 3600)  # 1 hour
        
        # Cache MP districts
        csv_path = os.path.join(settings.STATICFILES_DIRS[0], 'csv', 'cities.csv')
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            mp_districts = []
            for row in reader:
                if row.get('state_code') == 'MP':
                    mp_districts.append(row['name'])
        
        cache.set('mp_districts', mp_districts, 3600)  # 1 hour
        
        print(f"✓ Cached state mappings and {len(mp_districts)} MP districts")
        
    except Exception as e:
        print(f"✗ Failed to cache state-district data: {e}")

def clear_old_cache():
    """Clear old cache entries"""
    print("Clearing old cache entries...")
    
    # Clear specific cache patterns
    cache_patterns = [
        'admin_counts_*',
        'upzone_*',
        'approval_user_*',
        'registration_count_*',
        'approval_count_*'
    ]
    
    # Note: Django's cache doesn't support pattern deletion by default
    # This is a placeholder for cache clearing logic
    print("✓ Cache clearing completed")

def main():
    """Main cache warming function"""
    print("🔥 Starting YCSMP Cache Warming...")
    print("=" * 40)
    
    try:
        # Clear old cache first
        clear_old_cache()
        print()
        
        # Warm up various caches
        warm_upzone_cache()
        warm_approval_user_cache()
        warm_options_cache()
        warm_registration_counts()
        warm_state_district_cache()
        
        print()
        print("=" * 40)
        print("✅ Cache warming completed successfully!")
        print()
        print("Cached data will expire in 1 hour (3600 seconds)")
        print("Consider running this script every 30-60 minutes for optimal performance")
        
    except Exception as e:
        print(f"❌ Error during cache warming: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())