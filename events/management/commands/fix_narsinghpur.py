from django.core.management.base import BaseCommand
from events.models_location import StateDistrict
from events.models import EventRegistration

class Command(BaseCommand):
    help = 'Fix Narsinghpur district name variations'

    def handle(self, *args, **options):
        self.stdout.write('Fixing Narsinghpur district variations...')
        
        try:
            # Delete wrong entries first
            StateDistrict.objects.filter(
                district_name__in=['Narsimhapur', 'Narsinghgarh']
            ).delete()
            
            # Update existing registrations
            EventRegistration.objects.filter(
                city__in=['Narsimhapur', 'Narsinghgarh']
            ).update(city='Narsinghpur')
            
            # Create correct entry if not exists
            StateDistrict.objects.get_or_create(
                state_code='MP',
                district_name='Narsinghpur',
                defaults={'state_name': 'Madhya Pradesh', 'is_active': True}
            )
            
            self.stdout.write(
                self.style.SUCCESS('Successfully fixed Narsinghpur district variations')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error fixing districts: {str(e)}')
            )