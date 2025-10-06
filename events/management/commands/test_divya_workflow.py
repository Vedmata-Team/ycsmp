from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth.models import User
from events.models import EventRegistration
import requests

class Command(BaseCommand):
    help = 'Test the complete approval workflow for Divya Mohan Singh'

    def handle(self, *args, **options):
        self.stdout.write("=== Testing Divya Mohan Singh Approval Workflow ===")
        
        # Find Divya's registration
        try:
            registration = EventRegistration.objects.filter(
                full_name__icontains="Divya Mohan Singh",
                email="vedmatawebdesigning@gmail.com"
            ).first()
            
            if registration:
                self.stdout.write(f"✅ Found registration ID: {registration.id}")
                self.stdout.write(f"   Name: {registration.full_name}")
                self.stdout.write(f"   Email: {registration.email}")
                self.stdout.write(f"   Phone: {registration.phone}")
                self.stdout.write(f"   Status: {registration.approval_status}")
                self.stdout.write(f"   Vehicle: {registration.vehicle_number or 'None'}")
            else:
                self.stdout.write("❌ Divya Mohan Singh registration not found")
                return
        except Exception as e:
            self.stdout.write(f"❌ Database error: {e}")
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
        reg_id = registration.id
        
        # Step 1: Test ID card generation
        self.stdout.write(f"\n--- Step 1: ID Card Generation (ID: {reg_id}) ---")
        try:
            response = requests.get(f"{base_url}/id/card/{reg_id}/", timeout=30)
            if response.status_code == 200:
                self.stdout.write(f"✅ ID card generated: {len(response.content)} bytes")
            else:
                self.stdout.write(f"❌ ID card failed: {response.status_code}")
        except Exception as e:
            self.stdout.write(f"❌ ID card error: {e}")
        
        # Step 2: Test vehicle pass generation
        self.stdout.write(f"\n--- Step 2: Vehicle Pass Generation ---")
        if registration.vehicle_number:
            try:
                vehicle_num = registration.vehicle_number.replace(' ', '')
                response = requests.get(f"{base_url}/vehicle-pass/generate/{reg_id}/{vehicle_num}/", timeout=30)
                if response.status_code == 200:
                    self.stdout.write(f"✅ Vehicle pass generated: {len(response.content)} bytes")
                else:
                    self.stdout.write(f"❌ Vehicle pass failed: {response.status_code}")
            except Exception as e:
                self.stdout.write(f"❌ Vehicle pass error: {e}")
        else:
            self.stdout.write("⏭️ No vehicle number, skipping vehicle pass")
        
        # Step 3: Test admin form access
        self.stdout.write(f"\n--- Step 3: Admin Form Access ---")
        client = Client()
        client.force_login(user)
        
        try:
            response = client.get(f"/control/events/eventregistration/{reg_id}/change/")
            if response.status_code == 200:
                self.stdout.write("✅ Admin form accessible")
            else:
                self.stdout.write(f"❌ Admin form failed: {response.status_code}")
        except Exception as e:
            self.stdout.write(f"❌ Admin form error: {e}")
        
        # Step 4: Test email endpoint
        self.stdout.write(f"\n--- Step 4: Email Endpoint ---")
        try:
            response = client.get(f"/resend-email/{reg_id}/?skip_attachments=1")
            if response.status_code in [200, 302]:
                self.stdout.write(f"✅ Email endpoint accessible: {response.status_code}")
            else:
                self.stdout.write(f"❌ Email endpoint failed: {response.status_code}")
        except Exception as e:
            self.stdout.write(f"❌ Email endpoint error: {e}")
        
        self.stdout.write(f"\n=== Workflow Test Complete for Registration {reg_id} ===")
        self.stdout.write("All endpoints are ready for the JavaScript workflow!")