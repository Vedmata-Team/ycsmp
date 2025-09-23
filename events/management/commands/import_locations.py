import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from events.models import Country, State, City

class Command(BaseCommand):
    help = 'Import location data from CSV files'

    def handle(self, *args, **options):
        self.stdout.write('Starting location data import...')
        
        # Import countries
        self.import_countries()
        
        # Import states
        self.import_states()
        
        # Import cities (only India for now)
        self.import_cities()
        
        self.stdout.write(self.style.SUCCESS('Location data imported successfully!'))

    def import_countries(self):
        csv_path = os.path.join(settings.STATICFILES_DIRS[0], 'csv', 'countries.csv')
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            countries_to_create = []
            
            for row in reader:
                if not Country.objects.filter(code=row['iso2']).exists():
                    countries_to_create.append(Country(
                        code=row['iso2'],
                        name=row['name']
                    ))
            
            if countries_to_create:
                Country.objects.bulk_create(countries_to_create, ignore_conflicts=True)
                self.stdout.write(f'Created {len(countries_to_create)} countries')

    def import_states(self):
        csv_path = os.path.join(settings.STATICFILES_DIRS[0], 'csv', 'states.csv')
        
        # Get India country
        india, _ = Country.objects.get_or_create(code='IN', defaults={'name': 'India'})
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            states_to_create = []
            
            for row in reader:
                if row['country_name'] == 'India':
                    if not State.objects.filter(code=row['state_code'], country=india).exists():
                        states_to_create.append(State(
                            code=row['state_code'],
                            name=row['name'],
                            country=india
                        ))
            
            if states_to_create:
                State.objects.bulk_create(states_to_create, ignore_conflicts=True)
                self.stdout.write(f'Created {len(states_to_create)} states')

    def import_cities(self):
        csv_path = os.path.join(settings.STATICFILES_DIRS[0], 'csv', 'cities.csv')
        
        # Check existing count
        existing_count = City.objects.count()
        self.stdout.write(f'Starting with {existing_count} existing cities')
        
        # Get all states for faster lookup
        states_dict = {state.name: state for state in State.objects.filter(country__code='IN')}
        
        cities_to_create = []
        batch_size = 1000
        processed = 0
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader):
                processed += 1
                if processed % 5000 == 0:
                    self.stdout.write(f'Processed {processed} rows...')
                    
                if row['country_name'] == 'India':
                    state_name = row['state_name']
                    if state_name in states_dict:
                        city_name = row['name']
                        state = states_dict[state_name]
                        
                        # Check if city already exists
                        if not City.objects.filter(name=city_name, state=state).exists():
                            cities_to_create.append(City(
                                name=city_name,
                                state=state
                            ))
                        
                        # Bulk create in batches
                        if len(cities_to_create) >= batch_size:
                            with transaction.atomic():
                                City.objects.bulk_create(cities_to_create, ignore_conflicts=True)
                            self.stdout.write(f'Created batch of {len(cities_to_create)} cities (Total processed: {processed})')
                            cities_to_create = []
                    else:
                        self.stdout.write(f'State not found: {state_name}')
            
            # Create remaining cities
            if cities_to_create:
                with transaction.atomic():
                    City.objects.bulk_create(cities_to_create, ignore_conflicts=True)
                self.stdout.write(f'Created final batch of {len(cities_to_create)} cities')