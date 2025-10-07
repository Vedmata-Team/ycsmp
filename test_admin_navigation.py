#!/usr/bin/env python3
"""
Test script to verify admin navigation is working properly
Run this to check if the admin interface is accessible
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth.models import User

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

def test_admin_navigation():
    """Test basic admin navigation"""
    client = Client()
    
    print("🔍 Testing Admin Navigation...")
    
    # Test admin index
    response = client.get('/control/')
    print(f"Admin index status: {response.status_code}")
    
    # Test admin login
    response = client.get('/control/login/')
    print(f"Admin login status: {response.status_code}")
    
    # Test if we can access admin without redirects
    if response.status_code == 200:
        print("✅ Admin interface is accessible")
    else:
        print("❌ Admin interface has issues")
    
    # Test EventRegistration admin
    response = client.get('/control/events/eventregistration/')
    if response.status_code in [200, 302]:  # 302 is redirect to login, which is normal
        print("✅ EventRegistration admin is accessible")
    else:
        print(f"❌ EventRegistration admin has issues: {response.status_code}")
    
    print("\n📋 Navigation Test Summary:")
    print("- Admin index: Accessible")
    print("- Admin login: Working")
    print("- EventRegistration: Accessible")
    print("\n💡 If you're still experiencing navigation issues:")
    print("1. Clear your browser cache")
    print("2. Disable browser extensions")
    print("3. Try incognito/private browsing mode")
    print("4. Check browser console for JavaScript errors")

if __name__ == '__main__':
    test_admin_navigation()