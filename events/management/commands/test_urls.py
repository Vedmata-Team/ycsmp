from django.core.management.base import BaseCommand
from django.urls import reverse, resolve

class Command(BaseCommand):
    help = 'Test URL patterns'

    def handle(self, *args, **options):
        self.stdout.write("=== Testing URL Patterns ===")
        
        # Test resend-email URL
        try:
            url = reverse('events:resend_email', args=[4301])
            self.stdout.write(f"✅ resend_email URL: {url}")
        except Exception as e:
            self.stdout.write(f"❌ resend_email URL error: {e}")
        
        # Test URL resolution
        test_urls = [
            '/resend-email/4301/',
            '/events/resend-email/4301/',
        ]
        
        for test_url in test_urls:
            try:
                resolver = resolve(test_url)
                self.stdout.write(f"✅ {test_url} -> {resolver.func.__name__}")
            except Exception as e:
                self.stdout.write(f"❌ {test_url} -> {e}")