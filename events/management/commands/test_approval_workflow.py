from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth.models import User
from events.models import EventRegistration
import requests

class Command(BaseCommand):
    help = 'Test the complete approval workflow'

    def handle(self, *args, **options):
        self.stdout.write("=== Testing Complete Approval Workflow ===")
        
        # Get test registration
        try:
            registration = EventRegistration.objects.get(id=4301)
            self.stdout.write(f"✅ Found registration: {registration.full_name}")
        except EventRegistration.DoesNotExist:
            self.stdout.write("❌ Registration 4301 not found")
            return
        
        # Get staff user
        try:
            user = User.objects.filter(is_staff=True).first()
            self.stdout.write(f"✅ Using staff user: {user.username}")
        except:
            self.stdout.write("❌ No staff user found")
            return
        
        # Test each step
        base_url = "http://127.0.0.1:8000"
        
        # Step 1: Test ID card generation
        self.stdout.write("\n--- Step 1: ID Card Generation ---")
        try:
            response = requests.get(f"{base_url}/id/card/4301/", timeout=30)
            if response.status_code == 200:
                self.stdout.write(f"✅ ID card generated: {len(response.content)} bytes")
            else:
                self.stdout.write(f"❌ ID card failed: {response.status_code}")
        except Exception as e:
            self.stdout.write(f"❌ ID card error: {e}")
        
        # Step 2: Test vehicle pass generation
        self.stdout.write("\n--- Step 2: Vehicle Pass Generation ---")
        if registration.vehicle_number:
            try:
                response = requests.get(f"{base_url}/vehicle-pass/generate/4301/{registration.vehicle_number}/", timeout=30)
                if response.status_code == 200:
                    self.stdout.write(f"✅ Vehicle pass generated: {len(response.content)} bytes")
                else:
                    self.stdout.write(f"❌ Vehicle pass failed: {response.status_code}")
            except Exception as e:
                self.stdout.write(f"❌ Vehicle pass error: {e}")
        else:
            self.stdout.write("⏭️ No vehicle number, skipping vehicle pass")
        
        # Step 3: Test approval processing (simulate)
        self.stdout.write("\n--- Step 3: Approval Processing ---")
        client = Client()
        client.force_login(user)
        
        try:
            # Get the change form
            response = client.get(f"/control/events/eventregistration/4301/change/")
            if response.status_code == 200:
                self.stdout.write("✅ Admin form accessible")
                
                # Simulate approval with skip_auto_email
                post_data = {
                    'approval_status': 'approved',
                    '_skip_auto_email': '1',
                    '_save': '1',
                    'csrfmiddlewaretoken': client.session.get('csrftoken', 'test')
                }
                
                # Note: This would actually change the registration, so we'll just test the form access
                self.stdout.write("✅ Approval form data prepared (not submitted in test)")
            else:
                self.stdout.write(f"❌ Admin form failed: {response.status_code}")
        except Exception as e:
            self.stdout.write(f"❌ Approval processing error: {e}")
        
        # Step 4: Test email endpoint
        self.stdout.write("\n--- Step 4: Email Endpoint ---")
        try:
            response = client.get(f"/resend-email/4301/?skip_attachments=1")
            if response.status_code in [200, 302]:
                self.stdout.write(f"✅ Email endpoint accessible: {response.status_code}")
            else:
                self.stdout.write(f"❌ Email endpoint failed: {response.status_code}")
        except Exception as e:
            self.stdout.write(f"❌ Email endpoint error: {e}")
        
        self.stdout.write("\n=== Workflow Test Complete ===")
        self.stdout.write("Note: This test only checks endpoint accessibility, not actual processing")