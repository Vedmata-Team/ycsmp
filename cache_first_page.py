#!/usr/bin/env python3
"""
Cache first page results for instant admin loading
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.core.cache import cache
from events.models import EventRegistration

def cache_first_page():
    """Cache the first page of results for instant loading"""
    print("Caching first page results...")
    
    # Cache first 10 registrations (what admin shows first)
    first_page = list(EventRegistration.objects.select_related(
        'event', 'responsibility'
    ).only(
        'id', 'registration_number', 'full_name', 'city', 'approval_status',
        'registration_type', 'email', 'registration_date', 'event__title', 'responsibility__name'
    ).order_by('-registration_date')[:10])
    
    cache.set('admin_first_page', first_page, 300)  # 5 minutes
    print(f"✓ Cached first page with {len(first_page)} registrations")
    
    # Cache pending registrations page
    pending_page = list(EventRegistration.objects.filter(
        approval_status='pending'
    ).select_related('event').only(
        'id', 'registration_number', 'full_name', 'city', 'approval_status', 'event__title'
    ).order_by('-registration_date')[:10])
    
    cache.set('admin_pending_page', pending_page, 300)
    print(f"✓ Cached pending page with {len(pending_page)} registrations")

def main():
    print("⚡ Caching First Page Results")
    print("=" * 40)
    
    cache_first_page()
    
    print("\n" + "=" * 40)
    print("✅ First page caching completed!")
    print("\nAdmin interface should now load instantly!")
    print("Run this script every 5 minutes for best performance.")

if __name__ == "__main__":
    main()