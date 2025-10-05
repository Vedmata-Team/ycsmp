#!/usr/bin/env python
"""
Test script to debug vehicle verification URL routing issues
Run with: python test_vehicle_urls.py
"""

import os
import sys
import django
from django.conf import settings
from django.urls import reverse, resolve
from django.test import RequestFactory
from django.http import Http404

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

def test_url_patterns():
    """Test all vehicle pass URL patterns"""
    print("Testing Vehicle Pass URL Patterns...")
    print("=" * 50)
    
    # Test URLs
    test_urls = [
        '/vehicle-pass/generate/3757/MP09ZY8647/',
        '/vehicle-pass/preview/3757/MP09ZY8647/',
        '/vehicle-pass/verify/3757/MP09ZY8647/',
        '/vehicle-verify/3757/MP09ZY8647/',
    ]
    
    for url in test_urls:
        try:
            resolved = resolve(url)
            print(f"✓ {url}")
            print(f"   View: {resolved.func.__name__}")
            print(f"   Args: {resolved.args}")
            print(f"   Kwargs: {resolved.kwargs}")
        except Exception as e:
            print(f"✗ {url}")
            print(f"   Error: {str(e)}")
        print()

def test_reverse_urls():
    """Test reverse URL generation"""
    print("Testing Reverse URL Generation...")
    print("=" * 50)
    
    try:
        # Test vehicle pass URLs
        generate_url = reverse('vehicle_pass:generate', args=[3757, 'MP09ZY8647'])
        print(f"✓ Generate URL: {generate_url}")
        
        preview_url = reverse('vehicle_pass:preview', args=[3757, 'MP09ZY8647'])
        print(f"✓ Preview URL: {preview_url}")
        
        verify_url = reverse('vehicle_pass:verify', args=[3757, 'MP09ZY8647'])
        print(f"✓ Verify URL: {verify_url}")
        
    except Exception as e:
        print(f"✗ Reverse URL Error: {str(e)}")

def test_view_import():
    """Test if views can be imported correctly"""
    print("Testing View Imports...")
    print("=" * 50)
    
    try:
        from vehicle_pass.views import vehicle_verify, generate_vehicle_pass, vehicle_pass_preview
        print("✓ All views imported successfully")
        print(f"   vehicle_verify: {vehicle_verify}")
        print(f"   generate_vehicle_pass: {generate_vehicle_pass}")
        print(f"   vehicle_pass_preview: {vehicle_pass_preview}")
    except ImportError as e:
        print(f"✗ Import Error: {str(e)}")

def test_url_conf():
    """Test URL configuration"""
    print("Testing URL Configuration...")
    print("=" * 50)
    
    from django.urls import get_resolver
    resolver = get_resolver()
    
    print("Main URL patterns:")
    for pattern in resolver.url_patterns:
        print(f"  - {pattern.pattern}")
    
    print("\nVehicle Pass URL patterns:")
    try:
        from vehicle_pass.urls import urlpatterns
        for pattern in urlpatterns:
            print(f"  - {pattern.pattern}")
    except Exception as e:
        print(f"✗ Error loading vehicle_pass URLs: {str(e)}")

def test_database_connection():
    """Test if we can access the registration"""
    print("Testing Database Connection...")
    print("=" * 50)
    
    try:
        from events.models import EventRegistration
        registration = EventRegistration.objects.filter(id=3757).first()
        if registration:
            print(f"✓ Registration found: {registration.full_name}")
            print(f"   Vehicle: {registration.vehicle_number}")
            print(f"   Status: {registration.approval_status}")
        else:
            print("✗ Registration 3757 not found")
    except Exception as e:
        print(f"✗ Database Error: {str(e)}")

if __name__ == "__main__":
    print("Vehicle Pass URL Testing Tool")
    print("=" * 50)
    
    test_view_import()
    print()
    
    test_url_conf()
    print()
    
    test_url_patterns()
    print()
    
    test_reverse_urls()
    print()
    
    test_database_connection()
    print()
    
    print("Testing completed!")