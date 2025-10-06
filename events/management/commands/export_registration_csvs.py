from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import EventRegistration
from events.export_utils import ExportManager, REGISTRATION_FIELDS
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Export registrations to separate CSV files by registration type'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='exports',
            help='Output directory for CSV files (default: exports)'
        )
        parser.add_argument(
            '--event-id',
            type=int,
            help='Filter by specific event ID'
        )
        parser.add_argument(
            '--status',
            type=str,
            choices=['pending', 'district_approved', 'upzone_approved', 'approved', 'rejected'],
            help='Filter by approval status'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        event_id = options.get('event_id')
        status = options.get('status')
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Base queryset
        queryset = EventRegistration.objects.all()
        
        # Apply filters
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        if status:
            queryset = queryset.filter(approval_status=status)
        
        # Registration types to export
        registration_types = [
            ('participant', 'प्रतिभागी'),
            ('volunteer', 'समयदानी कार्यकर्ता'),
            ('organization_representative', 'संगठन प्रतिनिधि')
        ]
        
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        total_exported = 0
        
        self.stdout.write(self.style.SUCCESS('🚀 Starting CSV export...'))
        
        for reg_type, hindi_name in registration_types:
            # Filter by registration type
            type_queryset = queryset.filter(registration_type=reg_type)
            count = type_queryset.count()
            
            if count == 0:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  No {hindi_name} registrations found')
                )
                continue
            
            # Generate filename
            filename = f'{reg_type}_registrations_{timestamp}.csv'
            filepath = os.path.join(output_dir, filename)
            
            try:
                # Use existing export logic
                response = ExportManager.export_to_csv(
                    type_queryset, 
                    f'{reg_type}_export', 
                    REGISTRATION_FIELDS
                )
                
                # Write to file
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                total_exported += count
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ {hindi_name}: {count} records exported to {filename}'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error exporting {hindi_name}: {str(e)}'
                    )
                )
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Export completed! Total records: {total_exported}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(f'📁 Files saved in: {os.path.abspath(output_dir)}')
        )