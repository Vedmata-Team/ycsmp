#!/usr/bin/env python
"""
Data Integrity Test for Heavy Usage Scenarios
Tests vibhag and campaign data saving under concurrent load
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration, VibhagOption, Event
from django.db import transaction
import threading
import time
import random

def test_concurrent_registrations():
    """Test concurrent volunteer registrations with vibhag selection"""
    print("🧪 Testing concurrent volunteer registrations...")
    
    # Get test data
    event = Event.objects.filter(is_published=True).first()
    if not event:
        print("❌ No active event found for testing")
        return False
    
    vibhags = list(VibhagOption.objects.filter(is_active=True))
    if not vibhags:
        print("❌ No vibhag options found for testing")
        return False
    
    campaigns = ['youth_connect', 'water_cleanliness', 'tree_ganga']
    
    def create_registration(thread_id):
        """Create a single registration in a thread"""
        try:
            with transaction.atomic():
                # Random vibhag selection (1-3 vibhags)
                selected_vibhags = random.sample([str(v.id) for v in vibhags], 
                                               random.randint(1, min(3, len(vibhags))))
                
                # Random campaign selection (always include youth_connect + 1-2 more)
                selected_campaigns = ['youth_connect'] + random.sample(
                    [c for c in campaigns if c != 'youth_connect'], 
                    random.randint(1, 2)
                )
                
                registration = EventRegistration.objects.create(
                    event=event,
                    registration_type='volunteer',
                    full_name=f'Test User {thread_id}',
                    phone=f'98765432{thread_id:02d}',
                    email=f'test{thread_id}@example.com',
                    date_of_birth='1990-01-01',
                    gender='M',
                    transport_mode='bus',
                    education='graduation',
                    village_taluka='Test Village',
                    state='Madhya Pradesh',
                    city='Bhopal',
                    arrival_date='2025-10-26',
                    interested_in_volunteering=True,
                    volunteering_details='Test volunteering',
                    selected_campaigns=selected_campaigns,
                    selected_vibhags=selected_vibhags
                )
                
                print(f"✅ Thread {thread_id}: Registration {registration.id} created")
                print(f"   Vibhags: {selected_vibhags}")
                print(f"   Campaigns: {selected_campaigns}")
                
                return registration.id
                
        except Exception as e:
            print(f"❌ Thread {thread_id}: Error - {str(e)}")
            return None
    
    # Create multiple threads for concurrent registrations
    threads = []
    results = []
    
    for i in range(10):  # 10 concurrent registrations
        thread = threading.Thread(target=lambda i=i: results.append(create_registration(i)))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    successful = len([r for r in results if r is not None])
    print(f"📊 Results: {successful}/10 registrations successful")
    
    return successful == 10

def test_data_integrity():
    """Test data integrity after saving"""
    print("\n🔍 Testing data integrity...")
    
    # Get recent registrations
    recent_regs = EventRegistration.objects.filter(
        registration_type='volunteer',
        full_name__startswith='Test User'
    ).order_by('-id')[:5]
    
    if not recent_regs:
        print("❌ No test registrations found")
        return False
    
    integrity_passed = True
    
    for reg in recent_regs:
        print(f"\n📋 Checking Registration {reg.id}:")
        
        # Check vibhag data integrity
        if reg.selected_vibhags:
            try:
                vibhag_ids = [int(vid) for vid in reg.selected_vibhags if str(vid).isdigit()]
                vibhags = VibhagOption.objects.filter(id__in=vibhag_ids)
                vibhag_names = [v.name for v in vibhags]
                
                print(f"   ✅ Vibhags: {reg.selected_vibhags} → {vibhag_names}")
                
                if len(vibhag_ids) != len(vibhags):
                    print(f"   ❌ Vibhag integrity issue: {len(vibhag_ids)} IDs but {len(vibhags)} found")
                    integrity_passed = False
                    
            except Exception as e:
                print(f"   ❌ Vibhag processing error: {e}")
                integrity_passed = False
        
        # Check campaign data integrity
        if reg.selected_campaigns:
            try:
                campaign_dict = dict(EventRegistration.CAMPAIGN_CHOICES)
                campaign_names = [campaign_dict.get(code, f"UNKNOWN:{code}") for code in reg.selected_campaigns]
                
                print(f"   ✅ Campaigns: {reg.selected_campaigns} → {campaign_names}")
                
                unknown_campaigns = [name for name in campaign_names if name.startswith("UNKNOWN:")]
                if unknown_campaigns:
                    print(f"   ❌ Unknown campaigns found: {unknown_campaigns}")
                    integrity_passed = False
                    
            except Exception as e:
                print(f"   ❌ Campaign processing error: {e}")
                integrity_passed = False
        
        # Test export methods
        try:
            vibhag_export = reg.get_vibhag_names()
            campaign_export = reg.get_campaign_names()
            print(f"   ✅ Export methods work: Vibhags='{vibhag_export}', Campaigns='{campaign_export}'")
        except Exception as e:
            print(f"   ❌ Export method error: {e}")
            integrity_passed = False
    
    return integrity_passed

def cleanup_test_data():
    """Clean up test registrations"""
    print("\n🧹 Cleaning up test data...")
    
    deleted_count = EventRegistration.objects.filter(
        full_name__startswith='Test User'
    ).delete()[0]
    
    print(f"✅ Deleted {deleted_count} test registrations")

def main():
    print("🚀 Starting Data Integrity Test for Heavy Usage\n")
    
    try:
        # Test 1: Concurrent registrations
        concurrent_success = test_concurrent_registrations()
        
        # Test 2: Data integrity check
        integrity_success = test_data_integrity()
        
        # Summary
        print(f"\n📊 Test Summary:")
        print(f"   Concurrent Registrations: {'✅ PASS' if concurrent_success else '❌ FAIL'}")
        print(f"   Data Integrity: {'✅ PASS' if integrity_success else '❌ FAIL'}")
        
        overall_success = concurrent_success and integrity_success
        print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
        
        # Cleanup
        cleanup_test_data()
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)