#!/usr/bin/env python3
"""
Debug script to identify admin navigation issues
Run this to check for common problems
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

def check_admin_setup():
    """Check admin configuration for issues"""
    print("🔍 Checking Admin Setup...")
    
    # Check static files
    static_files = [
        'static/admin/js/admin_navigation_fix.js',
        'static/admin/css/admin_fix.css'
    ]
    
    for file_path in static_files:
        full_path = os.path.join(settings.BASE_DIR, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
    
    # Check admin URLs
    from django.urls import reverse
    try:
        admin_url = reverse('admin:index')
        print(f"✅ Admin URL: {admin_url}")
        
        registration_url = reverse('admin:events_eventregistration_changelist')
        print(f"✅ Registration admin URL: {registration_url}")
    except Exception as e:
        print(f"❌ URL error: {e}")
    
    # Check for problematic JavaScript files
    problematic_js = [
        'static/admin/js/filter_persistence.js',
        'static/admin/js/bulk_approval_progress.js',
        'static/admin/js/final_approval_with_idcard.js'
    ]
    
    print("\n📋 JavaScript Files Status:")
    for js_file in problematic_js:
        full_path = os.path.join(settings.BASE_DIR, js_file)
        if os.path.exists(full_path):
            print(f"⚠️  {js_file} exists (might cause issues)")
        else:
            print(f"✅ {js_file} not found (good)")
    
    print("\n💡 Recommendations:")
    print("1. Clear browser cache and cookies")
    print("2. Try incognito/private browsing mode")
    print("3. Check browser console for JavaScript errors")
    print("4. Disable browser extensions temporarily")
    print("5. If issues persist, temporarily rename problematic JS files")
    
    print("\n🔧 Quick Fix Commands:")
    print("# Temporarily disable problematic JS files:")
    for js_file in problematic_js:
        print(f"# mv {js_file} {js_file}.disabled")

if __name__ == '__main__':
    check_admin_setup()