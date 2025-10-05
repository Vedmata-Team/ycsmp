#!/usr/bin/env python
"""
Test script to debug DOB verification system
Run with: python test_dob_verification.py
"""

import os
import sys
import django
from django.conf import settings
from django.test import RequestFactory, Client
from django.urls import reverse
from django.template.loader import render_to_string

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

def test_static_files():
    """Test if static files are accessible"""
    print("Testing Static Files...")
    print("=" * 50)
    
    static_files = [
        '/static/js/dob_verification.js',
        '/static/js/vehicle_pass_download.js',
    ]
    
    client = Client()
    for file_path in static_files:
        try:
            response = client.get(file_path)
            if response.status_code == 200:
                print(f"✓ {file_path} - Accessible")
            else:
                print(f"✗ {file_path} - Status: {response.status_code}")
        except Exception as e:
            print(f"✗ {file_path} - Error: {str(e)}")

def test_template_rendering():
    """Test if templates render with DOB data"""
    print("\nTesting Template Rendering...")
    print("=" * 50)
    
    try:
        from events.models import EventRegistration
        registration = EventRegistration.objects.filter(
            vehicle_number__isnull=False,
            vehicle_number__gt=''
        ).exclude(vehicle_number='').first()
        
        if not registration:
            print("✗ No registration with vehicle number found")
            return
            
        print(f"✓ Using registration: {registration.full_name}")
        print(f"✓ DOB: {registration.date_of_birth}")
        print(f"✓ Vehicle: {registration.vehicle_number}")
        
        # Test vehicle pass preview template
        try:
            context = {
                'registration': registration,
                'qr_code_base64': 'test_qr_code',
                'download_url': f'/vehicle-pass/generate/{registration.id}/{registration.vehicle_number}/',
            }
            
            html = render_to_string('vehicle_pass/vehicle_pass_preview.html', context)
            
            # Check if DOB is in the rendered HTML
            dob_str = registration.date_of_birth.strftime('%Y-%m-%d')
            if dob_str in html:
                print(f"✓ DOB ({dob_str}) found in template")
            else:
                print(f"✗ DOB ({dob_str}) NOT found in template")
                
            # Check if JavaScript is included
            if 'dob_verification.js' in html:
                print("✓ DOB verification script included")
            else:
                print("✗ DOB verification script NOT included")
                
            # Check if USER_DOB is set
            if 'window.USER_DOB' in html:
                print("✓ USER_DOB variable found")
            else:
                print("✗ USER_DOB variable NOT found")
                
        except Exception as e:
            print(f"✗ Template rendering error: {str(e)}")
            
    except Exception as e:
        print(f"✗ Database error: {str(e)}")

def test_url_patterns():
    """Test URL patterns for vehicle pass"""
    print("\nTesting URL Patterns...")
    print("=" * 50)
    
    try:
        from events.models import EventRegistration
        registration = EventRegistration.objects.filter(
            vehicle_number__isnull=False,
            vehicle_number__gt=''
        ).exclude(vehicle_number='').first()
        
        if not registration:
            print("✗ No registration found")
            return
            
        test_urls = [
            f'/vehicle-pass/preview/{registration.id}/{registration.vehicle_number}/',
            f'/vehicle-pass/generate/{registration.id}/{registration.vehicle_number}/',
            f'/vehicle-verify/{registration.id}/{registration.vehicle_number}/',
        ]
        
        client = Client()
        for url in test_urls:
            try:
                response = client.get(url)
                print(f"✓ {url} - Status: {response.status_code}")
                
                if response.status_code == 200:
                    # Check if DOB verification is in the response
                    content = response.content.decode('utf-8')
                    if 'dob_verification.js' in content:
                        print(f"  ✓ DOB verification script found")
                    else:
                        print(f"  ✗ DOB verification script missing")
                        
                    if 'USER_DOB' in content:
                        print(f"  ✓ USER_DOB variable found")
                    else:
                        print(f"  ✗ USER_DOB variable missing")
                        
            except Exception as e:
                print(f"✗ {url} - Error: {str(e)}")
                
    except Exception as e:
        print(f"✗ URL testing error: {str(e)}")

def test_javascript_content():
    """Test JavaScript file content"""
    print("\nTesting JavaScript Content...")
    print("=" * 50)
    
    js_file_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'dob_verification.js')
    
    try:
        with open(js_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for key functions
        checks = [
            ('DOBVerification class', 'class DOBVerification'),
            ('setupEventListeners method', 'setupEventListeners()'),
            ('interceptDownloadLinks method', 'interceptDownloadLinks()'),
            ('showVerificationModal method', 'showVerificationModal'),
            ('Modal creation', 'createModal'),
            ('DOB verification', 'verifyDOB'),
            ('Event listener setup', 'addEventListener'),
        ]
        
        for check_name, check_string in checks:
            if check_string in content:
                print(f"✓ {check_name} - Found")
            else:
                print(f"✗ {check_name} - Missing")
                
        # Check file size
        file_size = len(content)
        print(f"✓ JavaScript file size: {file_size} characters")
        
    except FileNotFoundError:
        print(f"✗ JavaScript file not found: {js_file_path}")
    except Exception as e:
        print(f"✗ JavaScript file error: {str(e)}")

def test_template_blocks():
    """Test if template blocks are properly structured"""
    print("\nTesting Template Structure...")
    print("=" * 50)
    
    template_files = [
        'templates/vehicle_pass/vehicle_pass_preview.html',
        'templates/vehicle_pass/vehicle_verify.html',
    ]
    
    for template_file in template_files:
        template_path = os.path.join(settings.BASE_DIR, template_file)
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            print(f"\n{template_file}:")
            
            # Check for required blocks and elements
            checks = [
                ('extra_js block', '{% block extra_js %}'),
                ('USER_DOB variable', 'window.USER_DOB'),
                ('dob_verification.js', 'dob_verification.js'),
                ('download-protected class', 'download-protected'),
                ('download button', 'download-btn'),
            ]
            
            for check_name, check_string in checks:
                if check_string in content:
                    print(f"  ✓ {check_name}")
                else:
                    print(f"  ✗ {check_name}")
                    
        except FileNotFoundError:
            print(f"✗ Template file not found: {template_path}")
        except Exception as e:
            print(f"✗ Template file error: {str(e)}")

def test_browser_console_simulation():
    """Simulate browser console errors"""
    print("\nBrowser Console Simulation...")
    print("=" * 50)
    
    print("Common JavaScript issues to check in browser:")
    print("1. Open browser Developer Tools (F12)")
    print("2. Go to Console tab")
    print("3. Look for these errors:")
    print("   - 'dob_verification.js:1 Uncaught SyntaxError'")
    print("   - 'USER_DOB is not defined'")
    print("   - '404 Not Found: /static/js/dob_verification.js'")
    print("   - 'DOBVerification is not a constructor'")
    print("4. Check Network tab for failed resource loads")
    print("5. Verify that clicking download button shows modal")

if __name__ == "__main__":
    print("DOB Verification System Testing Tool")
    print("=" * 50)
    
    test_static_files()
    test_template_rendering()
    test_url_patterns()
    test_javascript_content()
    test_template_blocks()
    test_browser_console_simulation()
    
    print("\n" + "=" * 50)
    print("Testing completed!")
    print("\nIf issues found:")
    print("1. Check browser console for JavaScript errors")
    print("2. Verify static files are served correctly")
    print("3. Ensure templates include the verification script")
    print("4. Test with browser developer tools")