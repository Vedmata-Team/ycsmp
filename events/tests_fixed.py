from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Event, EventRegistration
from .forms import EventRegistrationForm

class EventModelTest(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            venue="Test Venue",
            event_date=timezone.now() + timedelta(days=30),
            registration_deadline=timezone.now() + timedelta(days=20),
            max_participants=100,
            category="test",
            district="Test District",
            is_published=True,
            is_featured=True
        )

    def test_event_creation(self):
        """Test event model creation"""
        self.assertEqual(self.event.title, "Test Event")
        self.assertTrue(self.event.is_published)
        self.assertEqual(self.event.max_participants, 100)

    def test_available_spots(self):
        """Test available spots calculation"""
        self.assertEqual(self.event.available_spots, 100)
        
        # Create a registration
        EventRegistration.objects.create(
            event=self.event,
            full_name="Test User",
            phone="9876543210",
            email="test@example.com",
            date_of_birth="1990-01-01",
            gender="M",
            education="graduation",
            village_taluka="Test Village",
            state="Madhya Pradesh",
            city="Bhopal",
            arrival_date="2025-10-25",
            approval_status="approved"
        )
        
        # Refresh from database
        self.event.refresh_from_db()
        self.assertEqual(self.event.available_spots, 99)

class EventRegistrationModelTest(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            venue="Test Venue",
            event_date=timezone.now() + timedelta(days=30),
            registration_deadline=timezone.now() + timedelta(days=20),
            max_participants=100,
            category="test",
            district="Test District",
            is_published=True
        )

    def test_registration_creation(self):
        """Test registration model creation"""
        registration = EventRegistration.objects.create(
            event=self.event,
            full_name="Test User",
            phone="9876543210",
            email="test@example.com",
            date_of_birth="1990-01-01",
            gender="M",
            education="graduation",
            village_taluka="Test Village",
            state="Madhya Pradesh",
            city="Bhopal",
            arrival_date="2025-10-25"
        )
        
        self.assertEqual(registration.full_name, "Test User")
        self.assertEqual(registration.approval_status, "pending")
        self.assertEqual(registration.registration_type, "participant")

    def test_registration_number_generation(self):
        """Test registration number generation"""
        # Test participant registration
        participant = EventRegistration.objects.create(
            event=self.event,
            full_name="Test Participant",
            phone="9876543210",
            email="participant@example.com",
            date_of_birth="1990-01-01",
            gender="M",
            education="graduation",
            village_taluka="Test Village",
            state="Madhya Pradesh",
            city="Bhopal",
            arrival_date="2025-10-25"
        )
        
        # Approve the registration to trigger number generation
        participant.approval_status = "approved"
        participant.save()
        participant.refresh_from_db()
        
        self.assertTrue(participant.registration_number.startswith("YCS"))
        
        # Test volunteer registration
        volunteer = EventRegistration.objects.create(
            event=self.event,
            full_name="Test Volunteer",
            phone="9876543211",
            email="volunteer@example.com",
            date_of_birth="1990-01-01",
            gender="F",
            education="graduation",
            village_taluka="Test Village",
            state="Madhya Pradesh",
            city="Bhopal",
            arrival_date="2025-10-25",
            registration_type="volunteer"
        )
        
        # Approve the registration to trigger number generation
        volunteer.approval_status = "approved"
        volunteer.save()
        volunteer.refresh_from_db()
        
        self.assertTrue(volunteer.registration_number.startswith("YCSV"))

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            venue="Test Venue",
            event_date=timezone.now() + timedelta(days=30),
            registration_deadline=timezone.now() + timedelta(days=20),
            max_participants=100,
            category="test",
            district="Test District",
            is_published=True,
            is_featured=True
        )

    def test_homepage_view(self):
        """Test homepage loads correctly"""
        response = self.client.get(reverse('events:homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "युवा चिंतन शिविर भोपाल")

    def test_events_list_view(self):
        """Test events list view"""
        response = self.client.get(reverse('events:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.title)

    def test_event_detail_view(self):
        """Test event detail view"""
        response = self.client.get(reverse('events:detail', kwargs={'pk': self.event.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.title)

    def test_registration_view_get(self):
        """Test registration form GET request"""
        response = self.client.get(reverse('events:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "पंजीकरण")

    def test_registration_view_post_valid(self):
        """Test registration form POST with valid data"""
        form_data = {
            'full_name': 'Test User',
            'phone': '9876543210',
            'email': 'test@example.com',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'education': 'graduation',
            'village_taluka': 'Test Village',
            'state': 'Madhya Pradesh',
            'city': 'Bhopal',
            'transport_mode': 'bus',
            'arrival_date': '2025-10-25',
            'previous_shivir': False,
            'interested_in_volunteering': False,
            'campaigns': ['youth_connect', 'health']
        }
        
        response = self.client.post(reverse('events:register'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        
        # Check if registration was created
        self.assertTrue(EventRegistration.objects.filter(phone='9876543210').exists())

    def test_volunteer_registration_view(self):
        """Test volunteer registration view"""
        response = self.client.get(reverse('events:volunteer_register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "समयदानी")

    def test_check_status_view(self):
        """Test check status view"""
        # Create a registration first
        registration = EventRegistration.objects.create(
            event=self.event,
            full_name="Test User",
            phone="9876543210",
            email="test@example.com",
            date_of_birth="1990-01-01",
            gender="M",
            education="graduation",
            village_taluka="Test Village",
            state="Madhya Pradesh",
            city="Bhopal",
            arrival_date="2025-10-25"
        )
        
        # Test GET request
        response = self.client.get(reverse('events:check_status'))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request with phone number
        response = self.client.post(reverse('events:check_status'), {'phone': '9876543210'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test User")

    def test_duplicate_registration_prevention(self):
        """Test that duplicate registrations are prevented"""
        # Create first registration
        EventRegistration.objects.create(
            event=self.event,
            full_name="Test User",
            phone="9876543210",
            email="test@example.com",
            date_of_birth="1990-01-01",
            gender="M",
            education="graduation",
            village_taluka="Test Village",
            state="Madhya Pradesh",
            city="Bhopal",
            arrival_date="2025-10-25"
        )
        
        # Try to create duplicate registration
        form_data = {
            'full_name': 'Test User 2',
            'phone': '9876543210',  # Same phone
            'email': 'test2@example.com',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'education': 'graduation',
            'village_taluka': 'Test Village',
            'state': 'Madhya Pradesh',
            'city': 'Bhopal',
            'transport_mode': 'bus',
            'arrival_date': '2025-10-25',
            'previous_shivir': False,
            'interested_in_volunteering': False,
            'campaigns': ['youth_connect', 'health']
        }
        
        response = self.client.post(reverse('events:register'), data=form_data)
        self.assertContains(response, "पहले से पंजीकरण है")

class SecurityTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_csrf_protection(self):
        """Test CSRF protection on forms"""
        form_data = {
            'full_name': 'Test User',
            'phone': '9876543210',
            'email': 'test@example.com'
        }
        
        # Create client that enforces CSRF
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        
        # POST without CSRF token should fail
        response = client.post(reverse('events:register'), data=form_data)
        self.assertEqual(response.status_code, 403)

    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        malicious_input = "'; DROP TABLE events_eventregistration; --"
        
        response = self.client.post(reverse('events:check_status'), {
            'phone': malicious_input
        })
        
        # Should not crash and should return normal response
        self.assertEqual(response.status_code, 200)

class PerformanceTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create multiple events for testing
        for i in range(10):
            Event.objects.create(
                title=f"Test Event {i}",
                description=f"Test Description {i}",
                venue=f"Test Venue {i}",
                event_date=timezone.now() + timedelta(days=30+i),
                registration_deadline=timezone.now() + timedelta(days=20+i),
                max_participants=100,
                category="test",
                district="Test District",
                is_published=True,
                is_featured=(i < 3)
            )

    def test_homepage_performance(self):
        """Test homepage loads efficiently with multiple events"""
        import time
        
        start_time = time.time()
        response = self.client.get(reverse('events:homepage'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        # Should load within 1 second
        self.assertLess(end_time - start_time, 1.0)

    def test_events_list_pagination(self):
        """Test events list pagination works correctly"""
        response = self.client.get(reverse('events:list'))
        self.assertEqual(response.status_code, 200)
        
        # Test with page parameter
        response = self.client.get(reverse('events:list') + '?page=1')
        self.assertEqual(response.status_code, 200)

class ErrorHandlingTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_404_error_page(self):
        """Test custom 404 error page"""
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)

    def test_invalid_event_id(self):
        """Test accessing non-existent event"""
        response = self.client.get(reverse('events:detail', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)

class MobileResponsivenessTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_mobile_user_agent(self):
        """Test mobile responsiveness"""
        mobile_headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        }
        
        response = self.client.get(reverse('events:homepage'), **mobile_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "viewport")  # Check for mobile viewport meta tag