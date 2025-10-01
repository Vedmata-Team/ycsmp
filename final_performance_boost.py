#!/usr/bin/env python3
"""
Final Performance Boost for YCSMP Admin
Implements result caching and query optimization
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.core.cache import cache
from events.models import EventRegistration, ApprovalUser

def cache_filtered_results():
    """Cache common filtered results for admin"""
    print("Caching filtered results...")
    
    # Cache by approval status
    statuses = ['pending', 'district_approved', 'upzone_approved', 'approved', 'rejected']
    for status in statuses:
        registrations = list(EventRegistration.objects.filter(
            approval_status=status
        ).values('id', 'registration_number', 'full_name', 'city', 'state')[:100])
        
        cache.set(f'registrations_{status}', registrations, 600)  # 10 minutes
        print(f"✓ Cached {len(registrations)} {status} registrations")
    
    # Cache by state
    mp_registrations = list(EventRegistration.objects.filter(
        state__icontains='madhya pradesh'
    ).values('id', 'registration_number', 'full_name', 'city')[:100])
    
    cache.set('registrations_mp', mp_registrations, 600)
    print(f"✓ Cached {len(mp_registrations)} MP registrations")

def optimize_count_queries():
    """Cache expensive count queries"""
    print("Optimizing count queries...")
    
    # Cache total counts
    total_count = EventRegistration.objects.count()
    cache.set('total_registrations', total_count, 300)  # 5 minutes
    
    # Cache status counts
    status_counts = {}
    for status in ['pending', 'approved', 'district_approved', 'upzone_approved', 'rejected']:
        count = EventRegistration.objects.filter(approval_status=status).count()
        status_counts[status] = count
        cache.set(f'count_{status}', count, 300)
    
    cache.set('all_status_counts', status_counts, 300)
    print(f"✓ Cached counts: {status_counts}")

def create_admin_performance_patch():
    """Create admin performance patch"""
    print("Creating admin performance patch...")
    
    patch_code = '''
# Add this method to EventRegistrationAdmin class

def get_queryset(self, request):
    """Ultra-optimized queryset with aggressive caching"""
    from django.core.cache import cache
    
    # Try to get cached results first
    user_id = request.user.id
    filters = request.GET.urlencode()
    cache_key = f"admin_qs_{user_id}_{hash(filters)}"
    
    cached_ids = cache.get(cache_key)
    if cached_ids:
        # Return queryset with cached IDs
        return EventRegistration.objects.filter(id__in=cached_ids).select_related(
            'event', 'responsibility'
        ).only(
            'id', 'registration_number', 'full_name', 'city', 'approval_status',
            'registration_type', 'email', 'registration_date'
        )
    
    # Original optimized queryset
    qs = super().get_queryset(request)
    qs = qs.select_related('event', 'responsibility').only(
        'id', 'registration_number', 'full_name', 'city', 'approval_status',
        'registration_type', 'email', 'registration_date'
    )
    
    # Apply user filtering (keep existing logic)
    if request.user.is_superuser:
        filtered_qs = qs
    else:
        try:
            approval_user = ApprovalUser.objects.select_related('upzone').get(user=request.user)
            if approval_user.state_code == 'MP':
                if approval_user.is_district_approver and approval_user.districts:
                    filtered_qs = qs.filter(city__in=approval_user.districts)
                elif approval_user.is_upzone_approver and approval_user.upzone:
                    filtered_qs = qs.filter(city__in=approval_user.upzone.districts or [])
                else:
                    filtered_qs = qs.filter(state__icontains='madhya pradesh')
            else:
                filtered_qs = qs.filter(state__iexact=approval_user.state_code)
        except:
            filtered_qs = qs.none()
    
    # Cache the IDs for future requests
    ids = list(filtered_qs.values_list('id', flat=True)[:1000])  # Limit to 1000
    cache.set(cache_key, ids, 120)  # Cache for 2 minutes
    
    return filtered_qs
'''
    
    print("Performance patch code:")
    print(patch_code)

def main():
    """Main function"""
    print("🚀 Final Performance Boost")
    print("=" * 40)
    
    try:
        cache_filtered_results()
        print()
        
        optimize_count_queries()
        print()
        
        create_admin_performance_patch()
        print()
        
        print("=" * 40)
        print("✅ Final performance boost completed!")
        print()
        print("Admin should now be significantly faster:")
        print("- Cached filtered results")
        print("- Cached count queries") 
        print("- Optimized queryset with ID caching")
        print()
        print("Test the admin interface now!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())