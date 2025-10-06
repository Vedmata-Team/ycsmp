#!/usr/bin/env python3
"""
Test script to verify the new vehicle pass download flow with progress tracking
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth.models import User

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration

def test_vehicle_download_flow():
    """Test the vehicle pass download flow"""
    print("🧪 Testing Vehicle Pass Download Flow")
    print("=" * 50)
    
    # Find a registration with vehicle information
    registration = EventRegistration.objects.filter(
        approval_status='approved',
        vehicle_number__isnull=False,
        transport_mode='car'
    ).exclude(
        vehicle_number__in=['', '-']
    ).first()
    
    if not registration:
        print("❌ No approved registrations with vehicle information found")
        return False
    
    print(f"✅ Found test registration: {registration.full_name}")
    print(f"   Vehicle: {registration.vehicle_number}")
    print(f"   Status: {registration.approval_status}")
    
    # Test the download URL
    client = Client()
    download_url = f"/vehicle-pass/generate/{registration.id}/{registration.vehicle_number}/"
    
    print(f"\n🔗 Testing download URL: {download_url}")
    
    try:
        response = client.get(download_url)
        
        if response.status_code == 200:
            print("✅ Download URL responds successfully")
            print(f"   Content-Type: {response.get('Content-Type', 'Not set')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            
            # Check if it's a valid PNG
            if response.content.startswith(b'\x89PNG'):
                print("✅ Response contains valid PNG data")
                return True
            else:
                print("❌ Response does not contain valid PNG data")
                return False
        else:
            print(f"❌ Download URL failed with status: {response.status_code}")
            if hasattr(response, 'content'):
                print(f"   Error: {response.content.decode()[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Download test failed with exception: {str(e)}")
        return False

def test_progress_javascript():
    """Test that the JavaScript file has the new progress methods"""
    print("\n🧪 Testing JavaScript Progress Implementation")
    print("=" * 50)
    
    js_file = "static/js/vehicle_pass_download.js"
    
    if not os.path.exists(js_file):
        print(f"❌ JavaScript file not found: {js_file}")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required methods
    required_methods = [
        'showProgressModal',
        'updateProgress',
        'delay',
        'async instantDownload'
    ]
    
    missing_methods = []
    for method in required_methods:
        if method not in content:
            missing_methods.append(method)
    
    if missing_methods:
        print(f"❌ Missing required methods: {', '.join(missing_methods)}")
        return False
    
    print("✅ All required progress methods found in JavaScript")
    
    # Check for progress steps
    progress_steps = [
        'Preparing download',
        'Generating vehicle pass',
        'Processing file',
        'Starting download',
        'Download completed'
    ]
    
    missing_steps = []
    for step in progress_steps:
        if step not in content:
            missing_steps.append(step)
    
    if missing_steps:
        print(f"❌ Missing progress steps: {', '.join(missing_steps)}")
        return False
    
    print("✅ All progress steps found in JavaScript")
    return True

def main():
    """Run all tests"""
    print("🚀 Vehicle Pass Download Flow Test Suite")
    print("=" * 60)
    
    # Test JavaScript implementation
    js_test = test_progress_javascript()
    
    # Test actual download flow
    download_test = test_vehicle_download_flow()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"JavaScript Progress Implementation: {'✅ PASS' if js_test else '❌ FAIL'}")
    print(f"Vehicle Download Flow: {'✅ PASS' if download_test else '❌ FAIL'}")
    
    if js_test and download_test:
        print("\n🎉 All tests passed! The new progress flow is ready.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)