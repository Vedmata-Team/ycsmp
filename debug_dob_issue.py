#!/usr/bin/env python
"""
Debug script to identify DOB verification issues
Run with: python debug_dob_issue.py
"""

import os
import sys
import django
from django.conf import settings
from django.test import Client
from django.template.loader import render_to_string

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

def test_dob_in_templates():
    """Test how DOB is rendered in different templates"""
    print("Testing DOB Rendering in Templates...")
    print("=" * 60)
    
    try:
        from events.models import EventRegistration
        
        # Get a registration with vehicle number
        registration = EventRegistration.objects.filter(
            vehicle_number__isnull=False,
            vehicle_number__gt=''
        ).exclude(vehicle_number='').first()
        
        if not registration:
            print("❌ No registration with vehicle number found")
            return
            
        print(f"✓ Using registration: {registration.full_name}")
        print(f"✓ Raw DOB from database: {registration.date_of_birth}")
        print(f"✓ DOB type: {type(registration.date_of_birth)}")
        
        # Test different date formats
        if registration.date_of_birth:
            print(f"✓ DOB strftime Y-m-d: {registration.date_of_birth.strftime('%Y-%m-%d')}")
            print(f"✓ DOB isoformat: {registration.date_of_birth.isoformat()}")
            print(f"✓ DOB as string: {str(registration.date_of_birth)}")
        
        # Test template rendering for different pages
        templates_to_test = [
            ('vehicle_pass/vehicle_pass_preview.html', {
                'registration': registration,
                'qr_code_base64': 'test_qr',
                'download_url': f'/vehicle-pass/generate/{registration.id}/{registration.vehicle_number}/',
            }),
            ('vehicle_pass/vehicle_verify.html', {
                'registration': registration,
                'qr_code_base64': 'test_qr',
                'is_primary_user': True,
            }),
            ('ID/id_card.html', {
                'registration': registration,
            }),
            ('ID/preview_card.html', {
                'registration': registration,
                'qr_code_base64': 'test_qr',
                'download_png_url': f'/id/card/{registration.id}/?format=PNG',
                'download_jpg_url': f'/id/card/{registration.id}/?format=JPG',
            }),
        ]
        
        for template_name, context in templates_to_test:
            print(f"\n--- Testing {template_name} ---")
            try:
                html = render_to_string(template_name, context)
                
                # Check for USER_DOB in rendered HTML
                if 'window.USER_DOB' in html:
                    # Extract the USER_DOB value
                    start = html.find('window.USER_DOB = \'') + len('window.USER_DOB = \'')
                    end = html.find('\'', start)
                    if start > len('window.USER_DOB = \'') - 1 and end > start:
                        user_dob_value = html[start:end]
                        print(f"✓ USER_DOB found: '{user_dob_value}'")
                        
                        # Validate the date format
                        if user_dob_value and len(user_dob_value) == 10 and user_dob_value.count('-') == 2:
                            print(f"✓ USER_DOB format looks correct (YYYY-MM-DD)")
                        else:
                            print(f"❌ USER_DOB format looks incorrect: '{user_dob_value}'")
                    else:
                        print(f"❌ Could not extract USER_DOB value")
                else:
                    print(f"❌ USER_DOB not found in template")
                
                # Check for vehicle_pass_download.js
                if 'vehicle_pass_download.js' in html:
                    print(f"✓ vehicle_pass_download.js script included")
                else:
                    print(f"❌ vehicle_pass_download.js script NOT included")
                    
            except Exception as e:
                print(f"❌ Template rendering error: {str(e)}")
                
    except Exception as e:
        print(f"❌ Database error: {str(e)}")

def test_javascript_file():
    """Test if JavaScript file exists and has correct content"""
    print("\n" + "=" * 60)
    print("Testing JavaScript File...")
    print("=" * 60)
    
    js_file_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'vehicle_pass_download.js')
    
    try:
        with open(js_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f"✓ JavaScript file found: {js_file_path}")
        print(f"✓ File size: {len(content)} characters")
        
        # Check for key functions
        key_checks = [
            ('VehiclePassDownloader class', 'class VehiclePassDownloader'),
            ('userDOB property', 'this.userDOB'),
            ('window.USER_DOB reference', 'window.USER_DOB'),
            ('Date comparison logic', 'inputFormatted === userFormatted'),
            ('Multiple verification methods', 'Method 1: Direct string comparison'),
            ('Debug logging', 'console.log'),
        ]
        
        for check_name, check_string in key_checks:
            if check_string in content:
                print(f"✓ {check_name} - Found")
            else:
                print(f"❌ {check_name} - Missing")
                
    except FileNotFoundError:
        print(f"❌ JavaScript file not found: {js_file_path}")
    except Exception as e:
        print(f"❌ JavaScript file error: {str(e)}")

def test_url_access():
    """Test URL access and response content"""
    print("\n" + "=" * 60)
    print("Testing URL Access...")
    print("=" * 60)
    
    try:
        from events.models import EventRegistration
        
        registration = EventRegistration.objects.filter(
            vehicle_number__isnull=False,
            vehicle_number__gt=''
        ).exclude(vehicle_number='').first()
        
        if not registration:
            print("❌ No registration found")
            return
            
        test_urls = [
            f'/vehicle-pass/preview/{registration.id}/{registration.vehicle_number}/',
            f'/id/preview/{registration.id}/',
        ]
        
        client = Client()
        for url in test_urls:
            try:
                print(f"\n--- Testing {url} ---")
                response = client.get(url)
                print(f"✓ Status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.content.decode('utf-8')
                    
                    # Check for USER_DOB
                    if 'window.USER_DOB' in content:
                        start = content.find('window.USER_DOB = \'') + len('window.USER_DOB = \'')
                        end = content.find('\'', start)
                        if start > len('window.USER_DOB = \'') - 1 and end > start:
                            user_dob_value = content[start:end]
                            print(f"✓ USER_DOB in response: '{user_dob_value}'")
                        else:
                            print(f"❌ Could not extract USER_DOB from response")
                    else:
                        print(f"❌ USER_DOB not found in response")
                    
                    # Check for script inclusion
                    if 'vehicle_pass_download.js' in content:
                        print(f"✓ JavaScript file referenced in response")
                    else:
                        print(f"❌ JavaScript file NOT referenced in response")
                        
                else:
                    print(f"❌ Non-200 response: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ URL test error: {str(e)}")
                
    except Exception as e:
        print(f"❌ URL testing error: {str(e)}")

def generate_test_html():
    """Generate a test HTML file for manual testing"""
    print("\n" + "=" * 60)
    print("Generating Test HTML...")
    print("=" * 60)
    
    try:
        from events.models import EventRegistration
        
        registration = EventRegistration.objects.filter(
            vehicle_number__isnull=False,
            vehicle_number__gt=''
        ).exclude(vehicle_number='').first()
        
        if not registration:
            print("❌ No registration found")
            return
            
        test_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>DOB Verification Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .test-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ccc; }}
        .download-btn {{ padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>DOB Verification Test Page</h1>
    
    <div class="test-section">
        <h3>Registration Info</h3>
        <p><strong>Name:</strong> {registration.full_name}</p>
        <p><strong>DOB:</strong> {registration.date_of_birth}</p>
        <p><strong>Vehicle:</strong> {registration.vehicle_number}</p>
    </div>
    
    <div class="test-section">
        <h3>Test Download Button</h3>
        <a href="/vehicle-pass/generate/{registration.id}/{registration.vehicle_number}/" class="download-btn">Test Vehicle Pass Download</a>
    </div>
    
    <div class="test-section">
        <h3>Debug Info</h3>
        <button onclick="console.log('USER_DOB:', window.USER_DOB); alert('USER_DOB: ' + window.USER_DOB);">Check USER_DOB</button>
        <button onclick="console.log('VehiclePassDownloader:', typeof VehiclePassDownloader); alert('VehiclePassDownloader: ' + typeof VehiclePassDownloader);">Check Class</button>
    </div>
    
    <script>
        // Pass user DOB to JavaScript for verification
        window.USER_DOB = '{registration.date_of_birth.strftime('%Y-%m-%d')}';
        console.log('Test page USER_DOB set to:', window.USER_DOB);
    </script>
    <script src="/static/js/vehicle_pass_download.js"></script>
    
    <script>
        // Additional debugging
        window.addEventListener('load', function() {{
            console.log('Page loaded');
            console.log('USER_DOB:', window.USER_DOB);
            console.log('VehiclePassDownloader available:', typeof VehiclePassDownloader !== 'undefined');
        }});
    </script>
</body>
</html>
        """
        
        test_file_path = os.path.join(settings.BASE_DIR, 'debug_dob_test.html')
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_html)
            
        print(f"✓ Test HTML generated: {test_file_path}")
        print(f"✓ Open this file in browser to test DOB verification manually")
        print(f"✓ Expected USER_DOB: {registration.date_of_birth.strftime('%Y-%m-%d')}")
        
    except Exception as e:
        print(f"❌ Test HTML generation error: {str(e)}")

if __name__ == "__main__":
    print("DOB Verification Debug Tool")
    print("=" * 60)
    
    test_dob_in_templates()
    test_javascript_file()
    test_url_access()
    generate_test_html()
    
    print("\n" + "=" * 60)
    print("Debug completed!")
    print("\nNext steps:")
    print("1. Check the console output above for any issues")
    print("2. Open the generated debug_dob_test.html in browser")
    print("3. Open browser console (F12) and test the download button")
    print("4. Check if USER_DOB is set correctly and matches expected format")