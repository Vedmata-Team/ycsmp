from django.core.management.base import BaseCommand
from events.models_location import StateDistrict
from events.models import EventRegistration

class Command(BaseCommand):
    help = 'Populate StateDistrict model from existing registrations'

    def handle(self, *args, **options):
        self.stdout.write('Populating StateDistrict from existing registrations...')
        
        try:
            created_count = 0
            
            # Get unique state-district combinations from registrations
            registrations = EventRegistration.objects.values('state', 'city').distinct()
            
            for reg in registrations:
                state_name = reg['state']
                district_name = reg['city']
                
                if state_name and district_name:
                    # Generate state code from state name
                    state_code = 'MP' if 'madhya pradesh' in state_name.lower() else state_name[:2].upper()
                    
                    obj, created = StateDistrict.objects.get_or_create(
                        state_code=state_code,
                        district_name=district_name,
                        defaults={
                            'state_name': state_name,
                            'is_active': True
                        }
                    )
                    
                    if created:
                        created_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully populated StateDistrict: {created_count} created'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error populating StateDistrict: {str(e)}')
            )