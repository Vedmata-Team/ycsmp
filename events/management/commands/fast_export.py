from django.core.management.base import BaseCommand
from events.fast_export import export_manager
import uuid
import time

class Command(BaseCommand):
    help = 'Run fast export with optional filters'
    
    def add_arguments(self, parser):
        parser.add_argument('--approval-status', type=str, help='Filter by approval status')
        parser.add_argument('--state', type=str, help='Filter by state')
        parser.add_argument('--city', type=str, help='Filter by city')
        parser.add_argument('--registration-type', type=str, help='Filter by registration type')
        parser.add_argument('--event-id', type=int, help='Filter by event ID')
    
    def handle(self, *args, **options):
        filters = {}
        
        if options['approval_status']:
            filters['approval_status'] = options['approval_status']
        if options['state']:
            filters['state'] = options['state']
        if options['city']:
            filters['city'] = options['city']
        if options['registration_type']:
            filters['registration_type'] = options['registration_type']
        if options['event_id']:
            filters['event_id'] = options['event_id']
        
        self.stdout.write('Starting fast export...')
        
        export_id = str(uuid.uuid4())
        export_manager.start_export(export_id, filters)
        
        # Monitor progress
        while True:
            status = export_manager.get_export_status(export_id)
            
            if status['status'] == 'processing':
                progress = status.get('progress', 0)
                self.stdout.write(f'Progress: {progress}%')
            elif status['status'] == 'completed':
                self.stdout.write(
                    self.style.SUCCESS(f'Export completed! File: {status["filename"]}')
                )
                break
            elif status['status'] == 'failed':
                self.stdout.write(
                    self.style.ERROR(f'Export failed: {status["error"]}')
                )
                break
            
            time.sleep(2)