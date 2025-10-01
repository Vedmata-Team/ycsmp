#!/usr/bin/env python3
"""
Fast Admin Optimization for YCSMP
Implements aggressive caching and query optimizations for admin interface
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.core.cache import cache
from events.models import EventRegistration, ApprovalUser

def create_cached_count_methods():
    """Create cached count methods for admin"""
    print("Creating cached count methods...")
    
    admin_patch = '''
# Add this to EventRegistrationAdmin class in admin.py

def get_cached_count(self, request, queryset):
    """Get cached count for queryset"""
    from django.core.cache import cache
    
    # Create cache key based on user and filters
    user_id = request.user.id
    filters = request.GET.urlencode()
    cache_key = f"admin_count_{user_id}_{hash(filters)}"
    
    count = cache.get(cache_key)
    if count is None:
        count = queryset.count()
        cache.set(cache_key, count, 60)  # Cache for 1 minute
    
    return count

def changelist_view(self, request, extra_context=None):
    """Override changelist with caching"""
    extra_context = extra_context or {}
    
    # Get base queryset
    qs = self.get_queryset(request)
    
    # Cache common counts
    from django.core.cache import cache
    cache_key = f"admin_stats_{request.user.id}"
    
    stats = cache.get(cache_key)
    if not stats:
        stats = {
            'total_pending': qs.filter(approval_status='pending').count(),
            'total_approved': qs.filter(approval_status='approved').count(),
            'total_district_approved': qs.filter(approval_status='district_approved').count(),
            'total_upzone_approved': qs.filter(approval_status='upzone_approved').count(),
        }
        cache.set(cache_key, stats, 300)  # 5 minutes
    
    extra_context['admin_stats'] = stats
    return super().changelist_view(request, extra_context)
'''
    
    print("Admin optimization code:")
    print(admin_patch)

def optimize_admin_queries():
    """Pre-warm admin query cache"""
    print("Pre-warming admin query cache...")
    
    # Cache approval user lookups
    approval_users = list(ApprovalUser.objects.select_related('user', 'upzone').all())
    for user in approval_users:
        cache_key = f"approval_user_{user.user.id}"
        cache.set(cache_key, user, 3600)
    
    print(f"✓ Cached {len(approval_users)} approval users")
    
    # Cache common registration counts
    counts = {
        'total': EventRegistration.objects.count(),
        'pending': EventRegistration.objects.filter(approval_status='pending').count(),
        'approved': EventRegistration.objects.filter(approval_status='approved').count(),
        'district_approved': EventRegistration.objects.filter(approval_status='district_approved').count(),
        'upzone_approved': EventRegistration.objects.filter(approval_status='upzone_approved').count(),
    }
    
    cache.set('global_registration_counts', counts, 300)
    print(f"✓ Cached global registration counts: {counts}")

def create_lightweight_admin():
    """Create lightweight admin configuration"""
    print("Creating lightweight admin configuration...")
    
    lightweight_config = '''
# Replace in EventRegistrationAdmin for better performance

class EventRegistrationAdmin(admin.ModelAdmin):
    # Minimal list display for speed
    list_display = ('registration_number', 'full_name', 'city', 'approval_status')
    
    # Reduced filters
    list_filter = ('approval_status', 'registration_type', 'state')
    
    # Minimal search fields
    search_fields = ('full_name', 'email', 'registration_number')
    
    # Performance settings
    list_per_page = 10
    list_max_show_all = 50
    show_full_result_count = False
    preserve_filters = True
    
    # Optimized queryset
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Only select essential fields
        qs = qs.select_related('event', 'responsibility').only(
            'id', 'registration_number', 'full_name', 'city', 'approval_status',
            'registration_type', 'state', 'email', 'registration_date'
        )
        
        # Apply user filtering (existing logic)
        # ... keep existing filtering logic ...
        
        return qs
    
    # Simplified fieldsets for faster form loading
    fieldsets = (
        ('Basic Info', {
            'fields': ('registration_number', 'full_name', 'email', 'phone')
        }),
        ('Location', {
            'fields': ('city', 'state', 'village_taluka')
        }),
        ('Approval', {
            'fields': ('approval_status', 'rejection_reason')
        }),
    )
'''
    
    print("Lightweight admin configuration:")
    print(lightweight_config)

def main():
    """Main optimization function"""
    print("⚡ Fast Admin Optimization")
    print("=" * 40)
    
    try:
        create_cached_count_methods()
        print()
        
        optimize_admin_queries()
        print()
        
        create_lightweight_admin()
        print()
        
        print("=" * 40)
        print("✅ Fast admin optimizations completed!")
        print()
        print("Next steps:")
        print("1. Apply the admin code changes shown above")
        print("2. Restart Django server")
        print("3. Test admin performance")
        print("4. Consider using the lightweight admin config if needed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())