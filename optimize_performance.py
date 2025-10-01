#!/usr/bin/env python3
"""
Performance Optimization Script for YCSMP Registration System
Optimizes database queries, adds indexes, and improves data loading speed
"""

import os
import sys
import django
from django.db import connection, transaction
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration, ApprovalUser, UpZone, Event, ResponsibilityOption, VibhagOption

def create_database_indexes():
    """Create optimized database indexes for faster queries"""
    print("Creating database indexes...")
    
    with connection.cursor() as cursor:
        indexes = [
            # EventRegistration indexes for common queries
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_approval_status ON events_eventregistration(approval_status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_state_city ON events_eventregistration(state, city)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_registration_type ON events_eventregistration(registration_type)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_registration_date ON events_eventregistration(registration_date DESC)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_email_sent ON events_eventregistration(email_sent)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_is_confirmed ON events_eventregistration(is_confirmed)",
            
            # Composite indexes for admin filtering
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_state_approval ON events_eventregistration(state, approval_status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_city_approval ON events_eventregistration(city, approval_status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_type_approval ON events_eventregistration(registration_type, approval_status)",
            
            # Search indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_full_name ON events_eventregistration USING gin(to_tsvector('english', full_name))",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_email ON events_eventregistration(email)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_phone ON events_eventregistration(phone)",
            
            # ApprovalUser indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_approvaluser_state_code ON events_approvaluser(state_code)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_approvaluser_districts ON events_approvaluser USING gin(districts)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_approvaluser_user_id ON events_approvaluser(user_id)",
            
            # Event indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_event_date ON events_event(event_date DESC)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_event_published ON events_event(is_published)",
            
            # UpZone indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_upzone_districts ON events_upzone USING gin(districts)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_upzone_active ON events_upzone(is_active)",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"✓ Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
            except Exception as e:
                if "already exists" not in str(e):
                    print(f"✗ Failed to create index: {e}")

def optimize_settings():
    """Update Django settings for better performance"""
    print("Optimizing Django settings...")
    
    settings_updates = """
# Add these to your settings.py for better performance

# Database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 600
DATABASES['default']['OPTIONS'] = {
    'MAX_CONNS': 20,
    'OPTIONS': {
        'MAX_CONNS': 20,
    }
}

# Query optimization
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,  # Disable in production
}

# Admin pagination
ADMIN_PAGINATION_SIZE = 50

# Cache timeout
CACHE_TIMEOUT = 300  # 5 minutes

# Session optimization
SESSION_CACHE_ALIAS = 'default'
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
"""
    
    print("Settings to add to settings.py:")
    print(settings_updates)

def create_optimized_admin_methods():
    """Create optimized admin methods"""
    print("Creating optimized admin methods...")
    
    admin_optimizations = '''
# Add these methods to EventRegistrationAdmin in admin.py

def get_queryset(self, request):
    """Optimized queryset with select_related and prefetch_related"""
    qs = super().get_queryset(request)
    
    # Use select_related for foreign keys
    qs = qs.select_related(
        'event',
        'responsibility',
        'district_approver',
        'upzone_approver', 
        'final_approver'
    )
    
    # Apply user-specific filtering
    if request.user.is_superuser:
        return qs
    
    try:
        approval_user = ApprovalUser.objects.select_related('upzone').get(user=request.user)
        
        if approval_user.is_super_approver:
            return qs
        
        # Apply filters based on user permissions
        if approval_user.state_code == 'MP':
            if approval_user.is_district_approver and approval_user.districts:
                return qs.filter(
                    city__in=approval_user.districts,
                    state__in=['Madhya Pradesh', 'MP']
                )
            elif approval_user.is_upzone_approver and approval_user.upzone:
                return qs.filter(
                    city__in=approval_user.upzone.districts or [],
                    state__in=['Madhya Pradesh', 'MP']
                )
            elif approval_user.is_state_approver:
                return qs.filter(state__in=['Madhya Pradesh', 'MP'])
        
        elif approval_user.is_state_approver:
            return qs.filter(state__iexact=approval_user.state_code)
        
        return qs.none()
        
    except ApprovalUser.DoesNotExist:
        return qs.none()

def changelist_view(self, request, extra_context=None):
    """Optimized changelist with caching"""
    extra_context = extra_context or {}
    
    # Cache common counts
    from django.core.cache import cache
    cache_key = f"admin_counts_{request.user.id}"
    
    counts = cache.get(cache_key)
    if not counts:
        qs = self.get_queryset(request)
        counts = {
            'total': qs.count(),
            'pending': qs.filter(approval_status='pending').count(),
            'approved': qs.filter(approval_status='approved').count(),
        }
        cache.set(cache_key, counts, 300)  # 5 minutes
    
    extra_context['counts'] = counts
    return super().changelist_view(request, extra_context)
'''
    
    print("Admin optimizations to implement:")
    print(admin_optimizations)

def optimize_model_methods():
    """Create optimized model methods"""
    print("Creating optimized model methods...")
    
    model_optimizations = '''
# Add these optimized methods to EventRegistration model

@classmethod
def get_filtered_registrations(cls, user, filters=None):
    """Optimized method to get filtered registrations"""
    qs = cls.objects.select_related(
        'event', 'responsibility', 'district_approver', 
        'upzone_approver', 'final_approver'
    )
    
    if filters:
        qs = qs.filter(**filters)
    
    # Apply user-specific filtering
    try:
        approval_user = ApprovalUser.objects.select_related('upzone').get(user=user)
        
        if approval_user.is_super_approver:
            return qs
        
        if approval_user.state_code == 'MP':
            if approval_user.is_district_approver and approval_user.districts:
                qs = qs.filter(
                    city__in=approval_user.districts,
                    state__in=['Madhya Pradesh', 'MP']
                )
            elif approval_user.is_upzone_approver and approval_user.upzone:
                qs = qs.filter(
                    city__in=approval_user.upzone.districts or [],
                    state__in=['Madhya Pradesh', 'MP']
                )
            elif approval_user.is_state_approver:
                qs = qs.filter(state__in=['Madhya Pradesh', 'MP'])
        
        elif approval_user.is_state_approver:
            qs = qs.filter(state__iexact=approval_user.state_code)
        
        # Filter by allowed registration types
        if approval_user.allowed_registration_types:
            qs = qs.filter(registration_type__in=approval_user.allowed_registration_types)
        
        return qs
        
    except ApprovalUser.DoesNotExist:
        return cls.objects.none()

@property
def cached_upzone(self):
    """Cached upzone lookup"""
    from django.core.cache import cache
    cache_key = f"upzone_{self.city}_{self.state}"
    
    upzone = cache.get(cache_key)
    if upzone is None:
        upzone = self.get_upzone_for_district()
        cache.set(cache_key, upzone, 3600)  # 1 hour
    
    return upzone
'''
    
    print("Model optimizations to implement:")
    print(model_optimizations)

def create_cache_warming_script():
    """Create cache warming script"""
    print("Creating cache warming script...")
    
    cache_script = '''
# cache_warmer.py - Run this periodically to warm up caches

import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.core.cache import cache
from events.models import EventRegistration, UpZone, ApprovalUser

def warm_upzone_cache():
    """Warm up upzone cache"""
    print("Warming upzone cache...")
    upzones = UpZone.objects.filter(is_active=True)
    for upzone in upzones:
        for district in upzone.districts:
            cache_key = f"upzone_{district}_MP"
            cache.set(cache_key, upzone, 3600)
    print(f"Cached {upzones.count()} upzones")

def warm_approval_user_cache():
    """Warm up approval user cache"""
    print("Warming approval user cache...")
    users = ApprovalUser.objects.select_related('user', 'upzone').all()
    for user in users:
        cache_key = f"approval_user_{user.user.id}"
        cache.set(cache_key, user, 3600)
    print(f"Cached {users.count()} approval users")

if __name__ == "__main__":
    warm_upzone_cache()
    warm_approval_user_cache()
    print("Cache warming completed!")
'''
    
    with open('cache_warmer.py', 'w', encoding='utf-8') as f:
        f.write(cache_script)
    
    print("✓ Created cache_warmer.py")

def update_admin_settings():
    """Update admin.py with performance optimizations"""
    print("Updating admin.py with performance optimizations...")
    
    # Read current admin.py
    with open('events/admin.py', 'r', encoding='utf-8') as f:
        admin_content = f.read()
    
    # Add performance optimizations
    optimizations = '''
    # Performance optimizations
    list_per_page = 50
    list_max_show_all = 200
    preserve_filters = True
    
    def get_queryset(self, request):
        """Optimized queryset with select_related"""
        qs = super().get_queryset(request)
        
        # Use select_related for foreign keys to reduce database queries
        qs = qs.select_related(
            'event',
            'responsibility', 
            'district_approver',
            'upzone_approver',
            'final_approver'
        )
        
        # Apply existing filtering logic
        if request.user.is_superuser:
            return qs
        
        if request.user.has_perm('events.view_all_eventregistration'):
            return qs
        
        try:
            approval_user = ApprovalUser.objects.select_related('upzone').get(user=request.user)
            
            if approval_user.is_super_approver:
                return qs
            
            # Apply user-specific filtering with optimized queries
            if approval_user.state_code == 'MP':
                base_filter = models.Q(state__icontains='madhya pradesh') | models.Q(state__iexact='MP')
                
                if approval_user.is_district_approver and approval_user.districts:
                    filtered_qs = qs.filter(
                        city__in=approval_user.districts,
                        approval_status__in=['pending', 'district_approved', 'upzone_approved', 'approved']
                    ).filter(base_filter)
                    
                elif approval_user.is_upzone_approver and approval_user.upzone:
                    upzone_districts = approval_user.upzone.districts or []
                    if upzone_districts:
                        filtered_qs = qs.filter(city__in=upzone_districts).filter(base_filter)
                    else:
                        return qs.none()
                        
                elif approval_user.is_state_approver:
                    filtered_qs = qs.filter(base_filter)
                else:
                    return qs.none()
                
                # Apply registration type filter if specified
                if approval_user.allowed_registration_types:
                    filtered_qs = filtered_qs.filter(registration_type__in=approval_user.allowed_registration_types)
                
                return filtered_qs
            
            elif approval_user.is_state_approver:
                state_name = self.get_state_name_from_code(approval_user.state_code)
                if state_name:
                    return qs.filter(
                        models.Q(state__iexact=state_name) | models.Q(state__iexact=approval_user.state_code)
                    )
                else:
                    return qs.filter(state__iexact=approval_user.state_code)
            
            return qs.none()
                
        except ApprovalUser.DoesNotExist:
            return qs.none()
'''
    
    # Find the get_queryset method and replace it
    if 'def get_queryset(self, request):' in admin_content:
        # Replace existing method
        lines = admin_content.split('\n')
        new_lines = []
        skip_lines = False
        indent_level = 0
        
        for line in lines:
            if 'def get_queryset(self, request):' in line and 'EventRegistrationAdmin' in admin_content[:admin_content.find(line)]:
                # Found the method, replace it
                new_lines.append(line)
                new_lines.extend(optimizations.split('\n')[1:])  # Skip first empty line
                skip_lines = True
                indent_level = len(line) - len(line.lstrip())
                continue
            
            if skip_lines:
                current_indent = len(line) - len(line.lstrip()) if line.strip() else 0
                if line.strip() and current_indent <= indent_level and not line.strip().startswith('#'):
                    skip_lines = False
                    new_lines.append(line)
                # Skip the old method lines
                continue
            
            new_lines.append(line)
        
        admin_content = '\n'.join(new_lines)
    
    # Write back the updated admin.py
    with open('events/admin.py', 'w', encoding='utf-8') as f:
        f.write(admin_content)
    
    print("✓ Updated admin.py with performance optimizations")

def main():
    """Main optimization function"""
    print("🚀 Starting YCSMP Performance Optimization...")
    print("=" * 50)
    
    try:
        # 1. Create database indexes
        create_database_indexes()
        print()
        
        # 2. Update admin with optimizations
        update_admin_settings()
        print()
        
        # 3. Create cache warming script
        create_cache_warming_script()
        print()
        
        # 4. Show additional optimizations
        optimize_settings()
        print()
        
        optimize_model_methods()
        print()
        
        print("=" * 50)
        print("✅ Performance optimization completed!")
        print()
        print("Next steps:")
        print("1. Add the suggested settings to your settings.py")
        print("2. Run 'python cache_warmer.py' to warm up caches")
        print("3. Consider setting up a cron job to run cache_warmer.py every hour")
        print("4. Monitor your admin performance and adjust list_per_page if needed")
        print("5. Consider using Redis for caching in production")
        
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())