#!/usr/bin/env python3
"""
Database Index Creation Script for YCSMP
Creates optimized indexes for better query performance
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.db import connection

def create_performance_indexes():
    """Create database indexes for better performance"""
    print("Creating performance indexes...")
    
    with connection.cursor() as cursor:
        indexes = [
            # EventRegistration indexes for common admin queries
            {
                'name': 'idx_eventregistration_approval_status',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_approval_status ON events_eventregistration(approval_status)',
                'description': 'Approval status filtering'
            },
            {
                'name': 'idx_eventregistration_state_city',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_state_city ON events_eventregistration(state, city)',
                'description': 'State and city filtering'
            },
            {
                'name': 'idx_eventregistration_registration_type',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_registration_type ON events_eventregistration(registration_type)',
                'description': 'Registration type filtering'
            },
            {
                'name': 'idx_eventregistration_registration_date',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_registration_date ON events_eventregistration(registration_date DESC)',
                'description': 'Registration date ordering'
            },
            {
                'name': 'idx_eventregistration_email_sent',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_email_sent ON events_eventregistration(email_sent)',
                'description': 'Email sent status filtering'
            },
            {
                'name': 'idx_eventregistration_is_confirmed',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_is_confirmed ON events_eventregistration(is_confirmed)',
                'description': 'Confirmation status filtering'
            },
            
            # Composite indexes for complex queries
            {
                'name': 'idx_eventregistration_state_approval',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_state_approval ON events_eventregistration(state, approval_status)',
                'description': 'State and approval status filtering'
            },
            {
                'name': 'idx_eventregistration_city_approval',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_city_approval ON events_eventregistration(city, approval_status)',
                'description': 'City and approval status filtering'
            },
            {
                'name': 'idx_eventregistration_type_approval',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_type_approval ON events_eventregistration(registration_type, approval_status)',
                'description': 'Registration type and approval status filtering'
            },
            
            # Search indexes
            {
                'name': 'idx_eventregistration_email',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_email ON events_eventregistration(email)',
                'description': 'Email search'
            },
            {
                'name': 'idx_eventregistration_phone',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_phone ON events_eventregistration(phone)',
                'description': 'Phone search'
            },
            {
                'name': 'idx_eventregistration_full_name',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventregistration_full_name ON events_eventregistration(full_name)',
                'description': 'Full name search'
            },
            
            # ApprovalUser indexes
            {
                'name': 'idx_approvaluser_state_code',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_approvaluser_state_code ON events_approvaluser(state_code)',
                'description': 'Approval user state filtering'
            },
            {
                'name': 'idx_approvaluser_user_id',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_approvaluser_user_id ON events_approvaluser(user_id)',
                'description': 'Approval user lookup'
            },
            
            # Event indexes
            {
                'name': 'idx_event_date',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_event_date ON events_event(event_date DESC)',
                'description': 'Event date ordering'
            },
            {
                'name': 'idx_event_published',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_event_published ON events_event(is_published)',
                'description': 'Published event filtering'
            },
            
            # UpZone indexes
            {
                'name': 'idx_upzone_active',
                'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_upzone_active ON events_upzone(is_active)',
                'description': 'Active upzone filtering'
            },
        ]
        
        created_count = 0
        failed_count = 0
        
        for index in indexes:
            try:
                # Remove CONCURRENTLY for compatibility
                sql = index['sql'].replace('CONCURRENTLY ', '')
                cursor.execute(sql)
                print(f"✓ Created: {index['name']} - {index['description']}")
                created_count += 1
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"- Exists: {index['name']} - {index['description']}")
                else:
                    print(f"✗ Failed: {index['name']} - {e}")
                    failed_count += 1
        
        print(f"\nIndex creation summary:")
        print(f"✓ Created: {created_count}")
        print(f"- Already existed: {len(indexes) - created_count - failed_count}")
        print(f"✗ Failed: {failed_count}")

def analyze_table_stats():
    """Analyze table statistics for optimization"""
    print("\nAnalyzing table statistics...")
    
    with connection.cursor() as cursor:
        tables = [
            'events_eventregistration',
            'events_approvaluser',
            'events_event',
            'events_upzone'
        ]
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"📊 {table}: {count:,} records")
            except Exception as e:
                print(f"✗ Failed to analyze {table}: {e}")

def vacuum_analyze():
    """Run VACUUM ANALYZE for better query planning"""
    print("\nRunning VACUUM ANALYZE...")
    
    with connection.cursor() as cursor:
        try:
            cursor.execute("VACUUM ANALYZE events_eventregistration")
            cursor.execute("VACUUM ANALYZE events_approvaluser")
            cursor.execute("VACUUM ANALYZE events_event")
            cursor.execute("VACUUM ANALYZE events_upzone")
            print("✓ VACUUM ANALYZE completed")
        except Exception as e:
            print(f"✗ VACUUM ANALYZE failed: {e}")

def main():
    """Main optimization function"""
    print("🚀 Starting Database Optimization...")
    print("=" * 50)
    
    try:
        # Analyze current state
        analyze_table_stats()
        print()
        
        # Create indexes
        create_performance_indexes()
        print()
        
        # Vacuum and analyze
        vacuum_analyze()
        
        print()
        print("=" * 50)
        print("✅ Database optimization completed!")
        print()
        print("Next steps:")
        print("1. Run 'python cache_warmer.py' to warm up caches")
        print("2. Monitor query performance in admin")
        print("3. Consider running this script after major data changes")
        
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())