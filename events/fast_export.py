#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font
from collections import defaultdict
import threading
import time

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration, UpZone, ResponsibilityOption, VibhagOption, Event, ApprovalUser

class FastExportManager:
    def __init__(self):
        self.export_status = {}
        
    def start_export(self, export_id, filters=None):
        """Start export in background thread"""
        self.export_status[export_id] = {'status': 'processing', 'progress': 0}
        thread = threading.Thread(target=self._export_worker, args=(export_id, filters))
        thread.daemon = True
        thread.start()
        return export_id
    
    def get_export_status(self, export_id):
        """Get current export status"""
        return self.export_status.get(export_id, {'status': 'not_found'})
    
    def _export_worker(self, export_id, filters):
        """Background worker for export"""
        try:
            filename = self._export_registrations_fast(export_id, filters)
            self.export_status[export_id] = {
                'status': 'completed', 
                'progress': 100,
                'filename': filename,
                'download_url': f'/events/admin/download/{filename}'
            }
        except Exception as e:
            self.export_status[export_id] = {
                'status': 'failed', 
                'error': str(e)
            }
    
    def _export_registrations_fast(self, export_id, filters):
        """Fast export with chunked processing"""
        # Build queryset with filters
        queryset = EventRegistration.objects.select_related('event', 'responsibility')
        
        if filters:
            if filters.get('approval_status'):
                queryset = queryset.filter(approval_status=filters['approval_status'])
            if filters.get('state'):
                queryset = queryset.filter(state__icontains=filters['state'])
            if filters.get('city'):
                queryset = queryset.filter(city__icontains=filters['city'])
            if filters.get('registration_type'):
                queryset = queryset.filter(registration_type=filters['registration_type'])
            if filters.get('event_id'):
                queryset = queryset.filter(event_id=filters['event_id'])
            if filters.get('date_from'):
                queryset = queryset.filter(registration_date__gte=filters['date_from'])
            if filters.get('date_to'):
                queryset = queryset.filter(registration_date__lte=filters['date_to'])
        
        total_count = queryset.count()
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Registrations Export"
        
        # Headers
        headers = [
            'ID', 'Registration Number', 'Full Name', 'Email', 'Phone', 'Gender', 'Date of Birth',
            'Education', 'Occupation', 'Village/Taluka', 'City', 'State', 'Registration Type',
            'Event Title', 'Registration Date', 'Approval Status', 'Transport Mode', 'Vehicle Number',
            'Arrival Date', 'Volunteering Details', 'Selected Campaigns', 'Selected Vibhags', 'Responsibility'
        ]
        ws.append(headers)
        
        # Process in chunks to avoid memory issues
        chunk_size = 1000
        processed = 0
        
        for chunk_start in range(0, total_count, chunk_size):
            chunk = queryset[chunk_start:chunk_start + chunk_size]
            
            for reg in chunk:
                row_data = [
                    reg.id,
                    getattr(reg, 'registration_number', ''),
                    reg.full_name,
                    getattr(reg, 'email', ''),
                    getattr(reg, 'phone', ''),
                    reg.gender,
                    reg.date_of_birth,
                    getattr(reg, 'education', ''),
                    getattr(reg, 'occupation', ''),
                    getattr(reg, 'village_taluka', ''),
                    reg.city,
                    reg.state,
                    reg.get_registration_type_display(),
                    reg.event.title,
                    reg.registration_date.strftime('%Y-%m-%d %H:%M:%S'),
                    reg.get_approval_status_display(),
                    getattr(reg, 'transport_mode', ''),
                    getattr(reg, 'vehicle_number', ''),
                    getattr(reg, 'arrival_date', ''),
                    getattr(reg, 'volunteering_details', ''),
                    reg.get_campaign_names(),
                    reg.get_vibhag_names(),
                    reg.responsibility.name if reg.responsibility else ''
                ]
                ws.append(row_data)
                processed += 1
            
            # Update progress
            progress = int((processed / total_count) * 100)
            self.export_status[export_id]['progress'] = progress
            
            # Small delay to prevent overwhelming the system
            time.sleep(0.01)
        
        # Save file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"registrations_export_{timestamp}.xlsx"
        filepath = os.path.join('exports', filename)
        
        # Ensure exports directory exists
        os.makedirs('exports', exist_ok=True)
        
        wb.save(filepath)
        return filename

# Global export manager instance
export_manager = FastExportManager()