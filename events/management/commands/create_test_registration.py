from django.core.management.base import BaseCommand
from events.models import Event, EventRegistration
from datetime import datetime, date
import pytz

class Command(BaseCommand):
    help = 'Create test registration for UpZone testing'

    def handle(self, *args, **options):
        # Get or create an event
        event, created = Event.objects.get_or_create(
            title='Test Event',
            defaults={
                'description': 'Test event for UpZone testing',
                'category': 'Test',
                'venue': 'Test Venue',
                'event_date': datetime(2025, 12, 25, 10, 0, tzinfo=pytz.UTC),
                'registration_deadline': datetime(2025, 12, 20, 23, 59, tzinfo=pytz.UTC),
                'registration_fee': 0,
                'max_participants': 100
            }
        )
        self.stdout.write(f'Event: {event.title}')

        # Create test registration from Bhopal
        registration, created = EventRegistration.objects.get_or_create(
            email='test@bhopal.com',
            defaults={
                'event': event,
                'full_name': 'Test User Bhopal',
                'phone': '9876543210',
                'date_of_birth': date(1990, 1, 1),
                'gender': 'M',
                'education': 'graduation',
                'village_taluka': 'Test Village',
                'city': 'Bhopal',
                'state': 'Madhya Pradesh',
                'country': 'India',
                'transport_mode': 'car',
                'arrival_date': '2025-10-25',
                'approval_status': 'district_approved'
            }
        )

        if created:
            self.stdout.write(f'✅ Test registration created: {registration.full_name} from {registration.city}')
            self.stdout.write(f'   Status: {registration.approval_status}')
        else:
            # Update existing registration
            registration.approval_status = 'district_approved'
            registration.city = 'Bhopal'
            registration.state = 'Madhya Pradesh'
            registration.save()
            self.stdout.write(f'✅ Test registration updated: {registration.full_name}')

        self.stdout.write(f'Total registrations: {EventRegistration.objects.count()}')
        self.stdout.write(f'MP registrations: {EventRegistration.objects.filter(state__icontains="madhya").count()}')
        self.stdout.write(f'District approved: {EventRegistration.objects.filter(approval_status="district_approved").count()}')