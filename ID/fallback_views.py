from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import subprocess
import os
from . import views, alternative_views

def generate_id_card_with_fallback(request, registration_id):
    """Try wkhtmltopdf first, fallback to Selenium if not available"""
    
    # Check if wkhtmltoimage is available
    wkhtml_paths = [
        'wkhtmltoimage',
        '/usr/bin/wkhtmltoimage',
        '/usr/local/bin/wkhtmltoimage'
    ]
    
    for wkhtml_path in wkhtml_paths:
        try:
            result = subprocess.run([wkhtml_path, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"DEBUG: Using wkhtmltopdf for ID card {registration_id}")
                # Use wkhtmltopdf method
                return alternative_views.generate_id_card_wkhtmltopdf(request, registration_id)
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            continue
    
    print(f"DEBUG: wkhtmltopdf not found in PATH or standard locations")
    
    # Fallback to Selenium method
    try:
        print(f"DEBUG: Using Selenium for ID card {registration_id}")
        return views.generate_id_card(request, registration_id)
    except Exception as e:
        print(f"DEBUG: Selenium failed: {e}")
        return HttpResponse(
            f"ID card generation failed. Install wkhtmltopdf or Chrome/ChromeDriver. Error: {str(e)}", 
            status=503
        )