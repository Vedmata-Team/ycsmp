from django.core.management.base import BaseCommand
from events.models import EventRegistration
from collections import defaultdict
from django.db import connection
import tempfile
from django.template.loader import render_to_string
from django.conf import settings
import qrcode
import io
import base64
from PIL import Image
import os
import time
import subprocess

class Command(BaseCommand):
    help = 'Export all approved vehicle passes in organized folder structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='Vehicle_Pass_Export',
            help='Output directory for exported passes'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of passes to export (for testing)'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        limit = options.get('limit')
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Starting vehicle pass bulk export to: {output_dir}')
        )
        
        # Create base directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get registrations with vehicle numbers
        registrations = EventRegistration.objects.filter(
            approval_status='approved',
            transport_mode='car',
            vehicle_number__isnull=False
        ).exclude(
            vehicle_number__exact=''
        ).exclude(
            vehicle_number__exact='-'
        ).select_related('responsibility').prefetch_related('event').order_by('registration_type', 'state', 'city', 'id')
        
        if limit:
            registrations = registrations[:limit]
            self.stdout.write(f'📊 Limited to {limit} passes for testing')
        
        self.stdout.write(f'📊 Total passes to export: {registrations.count()}')
        
        # Group by type first
        type_groups = defaultdict(list)
        for reg in registrations:
            type_groups[reg.registration_type].append(reg)
        
        total_exported = 0
        total_failed = 0
        start_time = time.time()
        
        # Process in order: Participants, Volunteers, Organizations
        type_order = ['participant', 'volunteer', 'organization_representative']
        
        for reg_type in type_order:
            if reg_type not in type_groups:
                continue
                
            regs = type_groups[reg_type]
            folder_name = {
                'participant': 'Participants',
                'volunteer': 'Volunteers', 
                'organization_representative': 'Organizations'
            }[reg_type]
            
            type_path = os.path.join(output_dir, folder_name)
            os.makedirs(type_path, exist_ok=True)
            
            self.stdout.write(f'\n📂 {folder_name}: {len(regs)} passes')
            
            # Group by district within type
            district_groups = defaultdict(list)
            for reg in regs:
                district_groups[reg.city].append(reg)
            
            # Sort districts by registration number district code
            def get_district_code(district_name):
                sample_reg = district_groups[district_name][0]
                if sample_reg.registration_number:
                    parts = sample_reg.registration_number.split('-')
                    if len(parts) >= 3:
                        return parts[2]
                return district_name
            
            sorted_districts = sorted(district_groups.keys(), key=get_district_code)
            for district in sorted_districts:
                district_regs = district_groups[district]
                
                self.stdout.write(f'  📍 {district}: {len(district_regs)} passes')
                
                # Check if MP state for upzone grouping
                if district_regs[0].state_code == 'MP':
                    # Group by upzone within district
                    upzone_groups = defaultdict(list)
                    for reg in district_regs:
                        connection.ensure_connection()
                        try:
                            upzone = reg.get_upzone_for_district()
                            upzone_name = upzone.name if upzone else 'No_UpZone'
                        except:
                            upzone_name = 'No_UpZone'
                        upzone_groups[upzone_name].append(reg)
                    
                    # Sort upzones by registration number sequence
                    def get_upzone_sort_key(upzone_name):
                        sample_reg = upzone_groups[upzone_name][0]
                        if sample_reg.registration_number:
                            parts = sample_reg.registration_number.split('-')
                            if len(parts) >= 4:
                                try:
                                    return int(parts[3])
                                except ValueError:
                                    pass
                        return upzone_name
                    
                    sorted_upzones = sorted(upzone_groups.keys(), key=get_upzone_sort_key)
                    for upzone_name in sorted_upzones:
                        upzone_regs = upzone_groups[upzone_name]
                        self.stdout.write(f'    🏢 {upzone_name}: {len(upzone_regs)} passes')
                        
                        # Sort registrations within upzone by registration number
                        sorted_upzone_regs = sorted(upzone_regs, key=lambda r: r.registration_number or f'ZZZ{r.id}')
                        connection.close()
                        batch_results = self.generate_passes_batch(sorted_upzone_regs, type_path, district, upzone_name)
                        for i, (success, filename) in enumerate(batch_results, 1):
                            if success:
                                self.stdout.write(f'      ✅ {i}/{len(upzone_regs)}: {filename}')
                                total_exported += 1
                            else:
                                self.stdout.write(
                                    self.style.ERROR(f'      ❌ {i}/{len(upzone_regs)}: {filename}')
                                )
                                total_failed += 1
                else:
                    # Non-MP states
                    sorted_district_regs = sorted(district_regs, key=lambda r: r.registration_number or f'ZZZ{r.id}')
                    connection.close()
                    batch_results = self.generate_passes_batch(sorted_district_regs, type_path, district)
                    for i, (success, filename) in enumerate(batch_results, 1):
                        if success:
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
        self.stdout.write(f'✅ Successfully exported: {total_exported} passes')
        self.stdout.write(f'❌ Failed: {total_failed} passes')
        self.stdout.write(f'📁 Location: {os.path.abspath(output_dir)}')

    def generate_passes_batch(self, registrations, type_path, district, upzone_name=None):
        """Generate multiple passes with single Chrome instance"""
        results = []
        driver = None
        
        try:
            # No driver needed for wkhtmltoimage
            pass
            
            for reg in registrations:
                try:
                    # Clean vehicle number for filename
                    clean_vehicle = reg.vehicle_number.replace(' ', '_').replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
                    
                    if upzone_name:
                        filename = f"{district}_{upzone_name}_{reg.id}_{reg.registration_number or 'NO_REG'}_{clean_vehicle}.jpg"
                    else:
                        filename = f"{district}_{reg.id}_{reg.registration_number or 'NO_REG'}_{clean_vehicle}.jpg"
                    
                    filepath = os.path.join(type_path, filename)
                    
                    # Skip if file already exists
                    if os.path.exists(filepath):
                        results.append((True, f"SKIPPED: {filename}"))
                        continue
                    
                    if self.generate_single_pass(reg, filepath):
                        results.append((True, filename))
                    else:
                        results.append((False, filename))
                except Exception as e:
                    results.append((False, f"Error: {str(e)}"))
                    
        except Exception as e:
            for reg in registrations:
                # Clean vehicle number for filename
                clean_vehicle = reg.vehicle_number.replace(' ', '_').replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
                
                if upzone_name:
                    filename = f"{district}_{upzone_name}_{reg.id}_{reg.registration_number or 'NO_REG'}_{clean_vehicle}.jpg"
                else:
                    filename = f"{district}_{reg.id}_{reg.registration_number or 'NO_REG'}_{clean_vehicle}.jpg"
                filepath = os.path.join(type_path, filename)
                
                if os.path.exists(filepath):
                    results.append((True, f"SKIPPED: {filename}"))
                else:
                    results.append((self.generate_pass(reg, filepath), filename))
        finally:
            pass
                
        return results
    
    def generate_single_pass(self, registration, output_path):
        """Generate single pass using wkhtmltoimage"""
        try:
            # Get background image based on registration type
            if registration.registration_type == 'volunteer':
                bg_file = 'volunteers_pass.png'
                user_type_hindi = 'समयदानी कार्यकर्ता'
            elif registration.registration_type == 'organization_representative':
                bg_file = 'organization_pass.png'
                user_type_hindi = 'संगठन प्रतिनिधि'
            else:
                bg_file = 'participants_pass.png'
                user_type_hindi = 'प्रतिभागी'
            
            # Generate QR code
            vehicle_verify_url = f"https://ycsmp.in/vehicle-pass/verify/{registration.id}/{registration.vehicle_number}/"
            qr = qrcode.QRCode(version=1, box_size=12, border=3)
            qr.add_data(vehicle_verify_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = io.BytesIO()
            qr_img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Load background image
            static_dir = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT
            bg_path = os.path.join(static_dir, 'Vehicle_Pass', bg_file)
            
            try:
                with open(bg_path, 'rb') as f:
                    bg_image_base64 = base64.b64encode(f.read()).decode()
            except:
                bg_image_base64 = ""
            
            # Render HTML
            html_content = render_to_string('vehicle_pass/vehicle_pass_html.html', {
                'registration': registration,
                'qr_code_base64': qr_code_base64,
                'user_type_hindi': user_type_hindi,
                'bg_image_base64': bg_image_base64,
                'validity_date': '29 अक्टूबर 2025',
            })
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_html = f.name
            
            temp_image = temp_html.replace('.html', '.png')
            
            try:
                # Use wkhtmltoimage with Windows paths
                wkhtml_paths = [
                    'wkhtmltoimage',
                    r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe',
                    r'C:\wkhtmltopdf\bin\wkhtmltoimage.exe',
                    '/usr/bin/wkhtmltoimage',
                    '/usr/local/bin/wkhtmltoimage'
                ]
                wkhtml_cmd = None
                
                for path in wkhtml_paths:
                    try:
                        result = subprocess.run([path, '--version'], capture_output=True, timeout=5)
                        if result.returncode == 0:
                            wkhtml_cmd = path
                            break
                    except Exception:
                        continue
                
                if not wkhtml_cmd:
                    return False
                
                cmd = [
                    wkhtml_cmd,
                    '--width', '1181',
                    '--height', '591',
                    '--format', 'png',
                    '--quality', '100',
                    '--disable-javascript',
                    '--no-stop-slow-scripts',
                    temp_html,
                    temp_image
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    return False
                
                # Read and crop image (same as vehicle pass)
                with open(temp_image, 'rb') as f:
                    image_bytes = f.read()
                
                img = Image.open(io.BytesIO(image_bytes))
                if img.height < 591:
                    new_img = Image.new('RGB', (1181, 591), 'white')
                    new_img.paste(img, (0, 0))
                    cropped_img = new_img
                else:
                    cropped_img = img.crop((0, 0, 1181, 591))
                
                # Save as JPEG
                cropped_img = cropped_img.convert('RGB')
                cropped_img.save(output_path, 'JPEG', quality=95)
                
                return True
                
            finally:
                for temp_file in [temp_html, temp_image]:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                    
        except Exception as e:
            return False
    
    def generate_pass(self, registration, output_path):
        """Fallback method using same logic as generate_single_pass"""
        return self.generate_single_pass(registration, output_path)