#!/usr/bin/env python3
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration
from django.template.loader import render_to_string

# Get Dr Rajesh Amrute
user = EventRegistration.objects.get(id=934)
print(f"User: {user.full_name}")
print(f"DOB: {user.date_of_birth}")

# Test template rendering
context = {
    'registration': user,
    'qr_code_base64': 'test',
    'user_type_hindi': 'test',
    'bg_image_base64': 'test',
    'validity_date': 'test',
    'download_url': 'test',
    'qr_url': 'test',
}

# Render the template
try:
    html = render_to_string('vehicle_pass/vehicle_pass_preview.html', context)
    
    # Check if DOB is in the HTML
    dob_str = user.date_of_birth.strftime('%Y-%m-%d')
    if dob_str in html:
        print(f"✅ DOB {dob_str} found in rendered HTML")
        
        # Find the script tag
        if "window.USER_DOB" in html:
            print("✅ window.USER_DOB found in HTML")
            
            # Extract the line
            lines = html.split('\n')
            for i, line in enumerate(lines):
                if 'window.USER_DOB' in line:
                    print(f"Line {i+1}: {line.strip()}")
        else:
            print("❌ window.USER_DOB NOT found in HTML")
    else:
        print(f"❌ DOB {dob_str} NOT found in rendered HTML")
        
    # Save HTML for inspection
    with open('debug_template_output.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("📄 HTML saved to debug_template_output.html")
        
except Exception as e:
    print(f"❌ Template rendering failed: {e}")
    import traceback
    traceback.print_exc()