#!/usr/bin/env python3
"""
Test URL Resolution
"""

import os
import sys
import django

# Setup Django
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.urls import reverse, resolve
from django.test import RequestFactory

def test_resend_email_url():
    print("🔍 TESTING RESEND EMAIL URL")
    print("=" * 50)
    
    try:
        # Test URL reverse
        url = reverse('events:resend_email', args=[4308])
        print(f"✅ URL reverse successful: {url}")
        
        # Test URL resolve
        resolver = resolve(url)
        print(f"✅ URL resolve successful: {resolver.func.__name__}")
        print(f"   View: {resolver.func}")
        print(f"   Args: {resolver.args}")
        print(f"   Kwargs: {resolver.kwargs}")
        
        return True
        
    except Exception as e:
        print(f"❌ URL test failed: {e}")
        return False

if __name__ == "__main__":
    test_resend_email_url()