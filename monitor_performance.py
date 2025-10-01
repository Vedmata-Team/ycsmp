#!/usr/bin/env python3
"""
Performance Monitoring Script for YCSMP
Monitors database performance and provides optimization recommendations
"""

import os
import sys
import django
import time
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.db import connection
from django.core.cache import cache
from events.models import EventRegistration, ApprovalUser, UpZone, Event

def test_query_performance():
    """Test performance of common admin queries"""
    print("Testing query performance...")
    print("-" * 40)
    
    queries = [
        {
            'name': 'All registrations count',
            'query': lambda: EventRegistration.objects.count(),
            'target_ms': 100
        },
        {
            'name': 'Pending registrations',
            'query': lambda: EventRegistration.objects.filter(approval_status='pending').count(),
            'target_ms': 50
        },
        {
            'name': 'MP registrations',
            'query': lambda: EventRegistration.objects.filter(state__icontains='madhya pradesh').count(),
            'target_ms': 100
        },
        {
            'name': 'Recent registrations (last 100)',
            'query': lambda: list(EventRegistration.objects.select_related('event', 'responsibility').order_by('-registration_date')[:100]),
            'target_ms': 200
        },
        {
            'name': 'Approval users with upzones',
            'query': lambda: list(ApprovalUser.objects.select_related('user', 'upzone').all()),
            'target_ms': 50
        },
        {
            'name': 'Active upzones',
            'query': lambda: list(UpZone.objects.filter(is_active=True)),
            'target_ms': 20
        }
    ]
    
    results = []
    
    for query_test in queries:
        start_time = time.time()
        try:
            result = query_test['query']()
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            status = "✓" if duration_ms <= query_test['target_ms'] else "⚠"
            if duration_ms > query_test['target_ms'] * 2:
                status = "✗"
            
            print(f"{status} {query_test['name']}: {duration_ms:.1f}ms (target: {query_test['target_ms']}ms)")
            
            results.append({
                'name': query_test['name'],
                'duration_ms': duration_ms,
                'target_ms': query_test['target_ms'],
                'status': status
            })
            
        except Exception as e:
            print(f"✗ {query_test['name']}: ERROR - {e}")
            results.append({
                'name': query_test['name'],
                'duration_ms': -1,
                'target_ms': query_test['target_ms'],
                'status': "✗"
            })
    
    return results

def test_cache_performance():
    """Test cache performance"""
    print("\nTesting cache performance...")
    print("-" * 40)
    
    cache_tests = [
        {
            'key': 'test_performance',
            'value': {'test': 'data', 'timestamp': datetime.now().isoformat()},
            'timeout': 300
        }
    ]
    
    for test in cache_tests:
        try:
            # Test cache set
            start_time = time.time()
            cache.set(test['key'], test['value'], test['timeout'])
            set_time = (time.time() - start_time) * 1000
            
            # Test cache get
            start_time = time.time()
            cached_value = cache.get(test['key'])
            get_time = (time.time() - start_time) * 1000
            
            if cached_value == test['value']:
                print(f"✓ Cache set/get: {set_time:.1f}ms / {get_time:.1f}ms")
            else:
                print(f"✗ Cache data mismatch")
                
        except Exception as e:
            print(f"✗ Cache test failed: {e}")

def check_database_stats():
    """Check database statistics"""
    print("\nDatabase statistics...")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        try:
            # Check table sizes
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE schemaname = 'public' 
                AND tablename LIKE 'events_%'
                ORDER BY tablename, attname
                LIMIT 20
            """)
            
            stats = cursor.fetchall()
            if stats:
                print("Table statistics (top 20):")
                for stat in stats:
                    print(f"  {stat[1]}.{stat[2]}: distinct={stat[3]}, correlation={stat[4]}")
            else:
                print("No statistics available")
                
        except Exception as e:
            print(f"Database stats error: {e}")

def check_slow_queries():
    """Check for slow queries"""
    print("\nChecking for slow queries...")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        try:
            # Enable query logging temporarily
            cursor.execute("SELECT name, setting FROM pg_settings WHERE name LIKE '%log%query%'")
            settings = cursor.fetchall()
            
            print("Query logging settings:")
            for setting in settings:
                print(f"  {setting[0]}: {setting[1]}")
                
        except Exception as e:
            print(f"Slow query check error: {e}")

def generate_recommendations(query_results):
    """Generate performance recommendations"""
    print("\nPerformance Recommendations:")
    print("=" * 50)
    
    slow_queries = [q for q in query_results if q['duration_ms'] > q['target_ms'] * 1.5]
    
    if not slow_queries:
        print("✅ All queries are performing within acceptable limits!")
        return
    
    print("⚠ Slow queries detected:")
    for query in slow_queries:
        print(f"  - {query['name']}: {query['duration_ms']:.1f}ms (target: {query['target_ms']}ms)")
    
    print("\nRecommendations:")
    
    # Check if indexes are needed
    if any('count' in q['name'].lower() for q in slow_queries):
        print("1. 🔍 Run 'python create_indexes.py' to create missing indexes")
    
    if any('recent' in q['name'].lower() for q in slow_queries):
        print("2. 📊 Consider reducing admin list_per_page setting")
    
    if any('mp registrations' in q['name'].lower() for q in slow_queries):
        print("3. 🗂 Add composite index on (state, approval_status)")
    
    print("4. 🔥 Run 'python cache_warmer.py' to warm up caches")
    print("5. 🧹 Consider running VACUUM ANALYZE on the database")
    print("6. 📈 Monitor performance regularly with this script")

def main():
    """Main monitoring function"""
    print("📊 YCSMP Performance Monitor")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Test query performance
        query_results = test_query_performance()
        
        # Test cache performance
        test_cache_performance()
        
        # Check database stats
        check_database_stats()
        
        # Check slow queries
        check_slow_queries()
        
        # Generate recommendations
        generate_recommendations(query_results)
        
        print("\n" + "=" * 50)
        print("✅ Performance monitoring completed!")
        print("\nRun this script regularly to monitor performance trends.")
        
    except Exception as e:
        print(f"❌ Error during monitoring: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())