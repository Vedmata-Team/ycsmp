from django.core.management.base import BaseCommand
from events.models import EventRegistration, UpZone
from collections import defaultdict
import subprocess
import tempfile
from django.template.loader import render_to_string
from django.conf import settings
import qrcode
import io
import base64
from PIL import Image
import os
import time

class Command(BaseCommand):
    help = 'Export all approved ID cards in organized folder structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='ID_Cards_Export',
            help='Output directory for exported cards'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of cards to export (for testing)'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        limit = options.get('limit')
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Starting ID card bulk export to: {output_dir}')
        )
        
        # Create base directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get registrations
        registrations = EventRegistration.objects.filter(
            approval_status='approved'
        ).select_related('responsibility').order_by('registration_type', 'state', 'city', 'id')
        
        if limit:
            registrations = registrations[:limit]
            self.stdout.write(f'📊 Limited to {limit} cards for testing')
        
        self.stdout.write(f'📊 Total cards to export: {registrations.count()}')
        
        # Group by type
        type_groups = defaultdict(list)
        for reg in registrations:
            type_groups[reg.registration_type].append(reg)
        
        total_exported = 0
        total_failed = 0
        start_time = time.time()
        
        for reg_type, regs in type_groups.items():
            folder_name = {
                'participant': 'Participants',
                'volunteer': 'Volunteers', 
                'organization_representative': 'Organizations'
            }.get(reg_type, reg_type)
            
            type_path = os.path.join(output_dir, folder_name)
            os.makedirs(type_path, exist_ok=True)
            
            self.stdout.write(f'\n📂 {folder_name}: {len(regs)} cards')
            
            # Group by district
            district_groups = defaultdict(list)
            for reg in regs:
                district_groups[reg.city].append(reg)
            
            for district, district_regs in district_groups.items():
                district_path = os.path.join(type_path, district)
                os.makedirs(district_path, exist_ok=True)
                
                self.stdout.write(f'  📍 {district}: {len(district_regs)} cards')
                
                if district_regs[0].state_code == 'MP':
                    # MP - Group by upzone
                    upzone_groups = defaultdict(list)
                    for reg in district_regs:
                        upzone = reg.get_upzone_for_district()
                        upzone_name = upzone.name if upzone else 'No_UpZone'
                        upzone_groups[upzone_name].append(reg)
                    
                    for upzone_name, upzone_regs in upzone_groups.items():
                        upzone_path = os.path.join(district_path, upzone_name)
                        os.makedirs(upzone_path, exist_ok=True)
                        
                        self.stdout.write(f'    🏢 {upzone_name}: {len(upzone_regs)} cards')
                        
                        for i, reg in enumerate(upzone_regs, 1):
                            filename = f"{reg.id}_{reg.registration_number or 'NO_REG'}_{reg.full_name.replace(' ', '_')}.jpg"
                            filepath = os.path.join(upzone_path, filename)
                            
                            if self.generate_card(reg, filepath):
                                self.stdout.write(f'      ✅ {i}/{len(upzone_regs)}: {filename}')
                                total_exported += 1
                            else:
                                self.stdout.write(
                                    self.style.ERROR(f'      ❌ {i}/{len(upzone_regs)}: {filename}')
                                )
                                total_failed += 1
                else:
                    # Non-MP states
                    for i, reg in enumerate(district_regs, 1):
                        filename = f"{reg.id}_{reg.registration_number or 'NO_REG'}_{reg.full_name.replace(' ', '_')}.jpg"
                        filepath = os.path.join(district_path, filename)
                        
                        if self.generate_card(reg, filepath):
                            self.stdout.write(f'    ✅ {i}/{len(district_regs)}: {filename}')
                            total_exported += 1
                        else:
                            self.stdout.write(
                                self.style.ERROR(f'    ❌ {i}/{len(district_regs)}: {filename}')
                            )
                            total_failed += 1
        
        end_time = time.time()
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Export completed in {end_time - start_time:.2f} seconds!')
        )
        self.stdout.write(f'✅ Successfully exported: {total_exported} cards')
        self.stdout.write(f'❌ Failed: {total_failed} cards')
        self.stdout.write(f'📁 Location: {os.path.abspath(output_dir)}')

    def generate_card(self, registration, output_path):
        """Generate single ID card"""
        try:
            # Generate QR code
            profile_url = f"https://ycsmp.in{registration.get_profile_url()}"
            qr = qrcode.QRCode(version=1, box_size=5, border=2)
            qr.add_data(profile_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = io.BytesIO()
            qr_img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Background image
            bg_files = {
                'volunteer': 'Volunteers_ID Card_.png',
                'organization_representative': 'Organization_ID Card_.png',
                'participant': 'Participants_ID Card_.png'
            }
            bg_file = bg_files.get(registration.registration_type, 'Participants_ID Card_.png')
            
            bg_path = os.path.join(settings.STATICFILES_DIRS[0], 'ID_Card', bg_file)
            with open(bg_path, 'rb') as f:
                bg_image_base64 = base64.b64encode(f.read()).decode()
            
            residence_status = "आवंटित" if registration.approval_status == 'approved' else "आवंटित नहीं"
            
            # Render HTML
            html_content = render_to_string('ID/id_card_html.html', {
                'registration': registration,
                'qr_code_base64': qr_code_base64,
                'residence_status': residence_status,
                'bg_image_base64': bg_image_base64,
            })
            
            # Temp files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_html = f.name
            
            temp_png = temp_html.replace('.html', '.png')
            
            try:
                # wkhtmltoimage
                cmd = [
                    'wkhtmltoimage',
                    '--width', '833', '--height', '1240',
                    '--format', 'png', '--quality', '100',
                    '--disable-javascript', '--no-stop-slow-scripts',
                    temp_html, temp_png
                ]
                
                result = subprocess.run(cmd, capture_output=True, timeout=30)
                if result.returncode != 0:
                    return False
                
                # Convert to JPG
                img = Image.open(temp_png)
                img = img.convert('RGB')
                img.save(output_path, 'JPEG', quality=95)
                
                return True
                
            finally:
                for temp_file in [temp_html, temp_png]:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            return False