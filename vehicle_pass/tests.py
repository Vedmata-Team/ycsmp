from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from events.models import EventRegistration, Event
from django.contrib.auth.models import User
import os
import tempfile
from PIL import Image
import io

class VehiclePassTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test event
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            venue='Test Venue',
            event_date='2025-10-29 10:00:00',
            registration_deadline='2025-10-25 23:59:59'
        )
        
        # Create test registration
        self.registration = EventRegistration.objects.create(
            event=self.event,
            full_name='Test User',
            phone='9876543210',
            email='test@example.com',
            date_of_birth='1990-01-01',
            gender='M',
            village_taluka='Test Village',
            city='Test City',
            state='Test State',
            transport_mode='car',
            vehicle_number='MP09ZY8647',
            registration_type='volunteer',
            approval_status='approved'
        )
    
    def test_debug_static_paths(self):
        """Test to debug static file paths"""
        print(f"\n=== VEHICLE PASS DEBUG INFO ===")
        print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
        print(f"STATICFILES_DIRS: {getattr(settings, 'STATICFILES_DIRS', 'Not set')}")
        print(f"BASE_DIR: {getattr(settings, 'BASE_DIR', 'Not set')}")
        
        # Check if Vehicle_Pass directory exists
        static_dirs = []
        if settings.STATIC_ROOT:
            static_dirs.append(settings.STATIC_ROOT)
        if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
            static_dirs.extend(settings.STATICFILES_DIRS)
        
        for static_dir in static_dirs:
            vehicle_pass_dir = os.path.join(static_dir, 'Vehicle_Pass')
            print(f"\nChecking directory: {vehicle_pass_dir}")
            print(f"Directory exists: {os.path.exists(vehicle_pass_dir)}")
            
            if os.path.exists(vehicle_pass_dir):
                files = os.listdir(vehicle_pass_dir)
                print(f"Files in directory: {files}")
                
                # Check specific files
                for filename in ['volunteer.png', 'org_member.png', 'participant.png']:
                    filepath = os.path.join(vehicle_pass_dir, filename)
                    exists = os.path.exists(filepath)
                    size = os.path.getsize(filepath) if exists else 0
                    print(f"  {filename}: exists={exists}, size={size} bytes")
    
    def test_create_sample_background_images(self):
        """Create sample background images for testing"""
        # Get static directory
        static_dir = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT
        if not static_dir:
            self.skipTest("No static directory configured")
        
        vehicle_pass_dir = os.path.join(static_dir, 'Vehicle_Pass')
        os.makedirs(vehicle_pass_dir, exist_ok=True)
        
        # Create sample images (10cm x 5cm = 1134x567 pixels at 300 DPI)
        width, height = 1134, 567
        
        # Colors for different types
        colors = {
            'volunteer.png': '#990000',      # Red for volunteers
            'org_member.png': '#ff9900',     # Orange for organization
            'participant.png': '#0066cc'     # Blue for participants
        }
        
        for filename, color in colors.items():
            # Create image with colored background
            img = Image.new('RGB', (width, height), color)
            
            # Add header area (top 0.9cm = ~106 pixels)
            header_height = int(0.9 * 118)  # 118 pixels per cm at 300 DPI
            header_img = Image.new('RGB', (width, header_height), '#ff6b00')  # Orange header
            img.paste(header_img, (0, 0))
            
            # Save image
            filepath = os.path.join(vehicle_pass_dir, filename)
            img.save(filepath, 'PNG')
            print(f"Created sample image: {filepath}")
        
        print(f"Sample images created in: {vehicle_pass_dir}")
    
    def test_vehicle_pass_preview_access(self):
        """Test vehicle pass preview page access"""
        url = reverse('vehicle_pass:preview', args=[self.registration.id, self.registration.vehicle_number])
        response = self.client.get(url)
        
        print(f"\n=== PREVIEW TEST ===")
        print(f"URL: {url}")
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("Preview page loaded successfully")
            # Check if background image data is in context
            if hasattr(response, 'context') and response.context:
                bg_data = response.context.get('bg_image_base64', '')
                print(f"Background image data length: {len(bg_data)} characters")
                print(f"Has background data: {'Yes' if bg_data else 'No'}")
        else:
            print(f"Preview page failed to load: {response.content}")
    
    def test_vehicle_pass_generation_access(self):
        """Test vehicle pass generation access"""
        url = reverse('vehicle_pass:generate', args=[self.registration.id, self.registration.vehicle_number])
        response = self.client.get(url)
        
        print(f"\n=== GENERATION TEST ===")
        print(f"URL: {url}")
        print(f"Response status: {response.status_code}")
        print(f"Content type: {response.get('Content-Type', 'Not set')}")
        
        if response.status_code == 200:
            print("Vehicle pass generated successfully")
            print(f"Response size: {len(response.content)} bytes")
        else:
            print(f"Vehicle pass generation failed: {response.content}")
    
    def test_directory_permissions(self):
        """Test directory permissions and access"""
        static_dirs = []
        if settings.STATIC_ROOT:
            static_dirs.append(settings.STATIC_ROOT)
        if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
            static_dirs.extend(settings.STATICFILES_DIRS)
        
        print(f"\n=== DIRECTORY PERMISSIONS TEST ===")
        for static_dir in static_dirs:
            print(f"\nTesting directory: {static_dir}")
            print(f"Directory exists: {os.path.exists(static_dir)}")
            print(f"Directory readable: {os.access(static_dir, os.R_OK) if os.path.exists(static_dir) else False}")
            print(f"Directory writable: {os.access(static_dir, os.W_OK) if os.path.exists(static_dir) else False}")
            
            vehicle_pass_dir = os.path.join(static_dir, 'Vehicle_Pass')
            print(f"Vehicle_Pass dir exists: {os.path.exists(vehicle_pass_dir)}")
            print(f"Vehicle_Pass dir readable: {os.access(vehicle_pass_dir, os.R_OK) if os.path.exists(vehicle_pass_dir) else False}")