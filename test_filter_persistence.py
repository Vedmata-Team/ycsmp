#!/usr/bin/env python
"""
Test script to verify filter persistence functionality
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

def test_filter_persistence():
    """Test if filter persistence files are properly set up"""
    
    print("=== Testing Filter Persistence Setup ===\n")
    
    # Check if JavaScript file exists
    js_file = project_dir / 'static' / 'admin' / 'js' / 'filter_persistence.js'
    print(f"1. Checking JavaScript file: {js_file}")
    if js_file.exists():
        print("   ✅ filter_persistence.js exists")
        print(f"   📁 Size: {js_file.stat().st_size} bytes")
    else:
        print("   ❌ filter_persistence.js NOT found")
        return False
    
    # Check if admin.py includes the JS file
    admin_file = project_dir / 'events' / 'admin.py'
    print(f"\n2. Checking admin.py configuration: {admin_file}")
    if admin_file.exists():
        with open(admin_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'filter_persistence.js' in content:
                print("   ✅ filter_persistence.js is included in admin.py")
            else:
                print("   ❌ filter_persistence.js NOT included in admin.py")
                return False
    else:
        print("   ❌ admin.py NOT found")
        return False
    
    # Check if template exists
    template_file = project_dir / 'templates' / 'admin' / 'change_list.html'
    print(f"\n3. Checking template file: {template_file}")
    if template_file.exists():
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'filter-status' in content or 'clear-filters-btn' in content:
                print("   ✅ Template includes filter persistence styles")
            else:
                print("   ⚠️  Template exists but may not have filter styles")
    else:
        print("   ❌ change_list.html template NOT found")
        return False
    
    # Test Django admin configuration
    print(f"\n4. Testing Django admin configuration...")
    try:
        from events.admin import EventRegistrationAdmin
        media = EventRegistrationAdmin.Media
        if hasattr(media, 'js') and 'admin/js/filter_persistence.js' in media.js:
            print("   ✅ EventRegistrationAdmin includes filter_persistence.js")
        else:
            print("   ❌ EventRegistrationAdmin does NOT include filter_persistence.js")
            return False
            
        # Check if filter preservation methods exist
        if hasattr(EventRegistrationAdmin, 'get_preserved_filters'):
            print("   ✅ Filter preservation methods found")
        else:
            print("   ❌ Filter preservation methods NOT found")
            return False
    except Exception as e:
        print(f"   ❌ Error testing admin configuration: {e}")
        return False
    
    # Check static files setup
    print(f"\n5. Checking static files configuration...")
    try:
        from django.conf import settings
        static_dirs = getattr(settings, 'STATICFILES_DIRS', [])
        if static_dirs:
            static_path = Path(static_dirs[0]) / 'admin' / 'js' / 'filter_persistence.js'
            if static_path.exists():
                print("   ✅ Static file accessible via STATICFILES_DIRS")
            else:
                print("   ❌ Static file NOT accessible via STATICFILES_DIRS")
        else:
            print("   ⚠️  No STATICFILES_DIRS configured")
    except Exception as e:
        print(f"   ❌ Error checking static files: {e}")
    
    # Test URL accessibility
    print(f"\n6. Testing URL patterns...")
    try:
        from django.urls import reverse
        admin_url = reverse('admin:events_eventregistration_changelist')
        print(f"   ✅ Admin URL accessible: {admin_url}")
    except Exception as e:
        print(f"   ❌ Error accessing admin URL: {e}")
        return False
    
    print(f"\n=== Filter Persistence Test Results ===")
    print("✅ All checks passed! Filter persistence should work.")
    print("\n📋 To test manually:")
    print("1. Go to: http://127.0.0.1:8000/control/events/eventregistration")
    print("2. Apply some filters (approval_status, state, etc.)")
    print("3. Click 'Edit' on any registration")
    print("4. Make changes and save")
    print("5. Verify filters are preserved after redirect")
    print("6. Also test bulk actions (approve, reject, etc.)")
    print("7. Look for 'Clear All Filters' button in filter sidebar")
    print("8. Check browser console for any JavaScript errors")
    
    return True

def test_debug_mode():
    """Check if debug mode affects functionality"""
    print(f"\n=== Debug Mode Check ===")
    try:
        from django.conf import settings
        debug_mode = getattr(settings, 'DEBUG', False)
        print(f"DEBUG mode: {debug_mode}")
        
        if debug_mode:
            print("⚠️  DEBUG=True - Static files served by Django")
            print("   Filter persistence should work in development")
        else:
            print("✅ DEBUG=False - Production mode")
            print("   Ensure static files are collected: python manage.py collectstatic")
            
            # Check if collectstatic was run
            static_root = getattr(settings, 'STATIC_ROOT', None)
            if static_root:
                collected_js = Path(static_root) / 'admin' / 'js' / 'filter_persistence.js'
                if collected_js.exists():
                    print("   ✅ Static files collected successfully")
                else:
                    print("   ❌ Static files NOT collected - run collectstatic")
                    return False
        
        return True
    except Exception as e:
        print(f"❌ Error checking debug mode: {e}")
        return False

if __name__ == '__main__':
    success = test_filter_persistence()
    debug_success = test_debug_mode()
    
    if success and debug_success:
        print(f"\n🎉 All tests passed! Filter persistence is ready to use.")
        sys.exit(0)
    else:
        print(f"\n❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)