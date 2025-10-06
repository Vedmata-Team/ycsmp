#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('e:/Divy/Projects/GitHub/ycsmp')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')

# Setup Django
django.setup()

from django.urls import reverse, resolve
from django.test import RequestFactory
from events.views import resend_registration_email

def test_url_patterns():
    print("=== Testing URL Patterns ===")
    
    # Test if the URL pattern exists
    try:
        url = reverse('events:resend_email', args=[4301])
        print(f"✅ URL pattern found: {url}")
    except Exception as e:
        print(f"❌ URL pattern error: {e}")
    
    # Test URL resolution
    try:
        resolver = resolve('/events/resend-email/4301/')
        print(f"✅ URL resolves to: {resolver.func.__name__}")
        print(f"   View module: {resolver.func.__module__}")
        print(f"   URL name: {resolver.url_name}")
        print(f"   Namespace: {resolver.namespace}")
    except Exception as e:
        print(f"❌ URL resolution error: {e}")
    
    # Test the view function directly
    try:
        from events.models import EventRegistration
        from django.contrib.auth.models import User
        
        # Get a test registration
        registration = EventRegistration.objects.get(id=4301)
        print(f"✅ Found registration: {registration.full_name}")
        
        # Create a test user
        user = User.objects.filter(is_staff=True).first()
        print(f"✅ Using staff user: {user.username}")
        
        # Create a test request
        factory = RequestFactory()
        request = factory.get('/events/resend-email/4301/?skip_attachments=1')
        request.user = user
        
        # Test the view
        response = resend_registration_email(request, 4301)
        print(f"✅ View response status: {response.status_code}")
        
    except Exception as e:
        print(f"❌ View test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_url_patterns()