import os
import django
from django.conf import settings

# Simple Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from django.urls import reverse, resolve

print("=== URL Pattern Test ===")

# Test events URLs
try:
    # Test the resend-email URL
    url = reverse('events:resend_email', args=[4301])
    print(f"✅ resend_email URL: {url}")
except Exception as e:
    print(f"❌ resend_email URL error: {e}")

# Test URL resolution
test_urls = [
    '/events/resend-email/4301/',
    '/events/quick-email/4301/',
]

for test_url in test_urls:
    try:
        resolver = resolve(test_url)
        print(f"✅ {test_url} -> {resolver.func.__name__}")
    except Exception as e:
        print(f"❌ {test_url} -> {e}")

# Check events.urls patterns
try:
    from events import urls as events_urls
    print(f"\n=== Events URL Patterns ===")
    for pattern in events_urls.urlpatterns:
        print(f"Pattern: {pattern.pattern}")
        if hasattr(pattern, 'name'):
            print(f"  Name: {pattern.name}")
except Exception as e:
    print(f"❌ Error reading events URLs: {e}")