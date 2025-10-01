#!/usr/bin/env python3
"""
Additional Query Optimizations for YCSMP
Addresses specific slow query issues identified in monitoring
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.db import connection

def create_additional_indexes():
    """Create additional indexes for slow queries"""
    print("Creating additional performance indexes...")
    
    with connection.cursor() as cursor:
        additional_indexes = [
            # Partial indexes for better performance
            "CREATE INDEX IF NOT EXISTS idx_eventregistration_pending ON events_eventregistration(id) WHERE approval_status = 'pending'",
            "CREATE INDEX IF NOT EXISTS idx_eventregistration_approved ON events_eventregistration(id) WHERE approval_status = 'approved'",
            
            # Covering indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_eventregistration_list_view ON events_eventregistration(registration_date DESC, approval_status, registration_type)",
            
            # Foreign key indexes
            "CREATE INDEX IF NOT EXISTS idx_eventregistration_event_id ON events_eventregistration(event_id)",
            "CREATE INDEX IF NOT EXISTS idx_eventregistration_responsibility_id ON events_eventregistration(responsibility_id)",
            "CREATE INDEX IF NOT EXISTS idx_eventregistration_district_approver_id ON events_eventregistration(district_approver_id)",
            "CREATE INDEX IF NOT EXISTS idx_eventregistration_upzone_approver_id ON events_eventregistration(upzone_approver_id)",
            "CREATE INDEX IF NOT EXISTS idx_eventregistration_final_approver_id ON events_eventregistration(final_approver_id)",
            
            # ApprovalUser optimizations
            "CREATE INDEX IF NOT EXISTS idx_approvaluser_upzone_id ON events_approvaluser(upzone_id)",
        ]
        
        created = 0
        for sql in additional_indexes:
            try:
                cursor.execute(sql)
                print(f"✓ Created: {sql.split('idx_')[1].split(' ')[0]}")
                created += 1
            except Exception as e:
                if "already exists" not in str(e):
                    print(f"✗ Failed: {e}")
        
        print(f"\nCreated {created} additional indexes")

def optimize_database_settings():
    """Optimize PostgreSQL settings for better performance"""
    print("\nOptimizing database settings...")
    
    with connection.cursor() as cursor:
        optimizations = [
            "SET work_mem = '16MB'",
            "SET maintenance_work_mem = '64MB'",
            "SET effective_cache_size = '256MB'",
            "SET random_page_cost = 1.1",
        ]
        
        for sql in optimizations:
            try:
                cursor.execute(sql)
                print(f"✓ Applied: {sql}")
            except Exception as e:
                print(f"✗ Failed: {sql} - {e}")

def analyze_tables():
    """Run ANALYZE on all tables for better query planning"""
    print("\nAnalyzing tables for better query planning...")
    
    with connection.cursor() as cursor:
        tables = [
            'events_eventregistration',
            'events_approvaluser', 
            'events_upzone',
            'events_event',
            'events_responsibilityoption',
            'events_vibhagoption'
        ]
        
        for table in tables:
            try:
                cursor.execute(f"ANALYZE {table}")
                print(f"✓ Analyzed: {table}")
            except Exception as e:
                print(f"✗ Failed to analyze {table}: {e}")

def main():
    """Main optimization function"""
    print("🔧 Additional Query Optimizations")
    print("=" * 40)
    
    try:
        create_additional_indexes()
        optimize_database_settings()
        analyze_tables()
        
        print("\n" + "=" * 40)
        print("✅ Additional optimizations completed!")
        print("\nRecommendations:")
        print("1. Test admin performance now")
        print("2. Run monitor_performance.py to check improvements")
        print("3. Consider reducing list_per_page to 10-15 if still slow")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())