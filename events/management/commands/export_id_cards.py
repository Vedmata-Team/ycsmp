from django.core.management.base import BaseCommand
from events.models import EventRegistration, UpZone
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
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
        
        # Get registrations with prefetch to avoid DB queries during processing
        registrations = EventRegistration.objects.filter(
            approval_status='approved'
        ).select_related('responsibility').prefetch_related('event').order_by('registration_type', 'state', 'city', 'id')
        
        if limit:
            registrations = registrations[:limit]
            self.stdout.write(f'📊 Limited to {limit} cards for testing')
        
        self.stdout.write(f'📊 Total cards to export: {registrations.count()}')
        
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
            
            self.stdout.write(f'\n📂 {folder_name}: {len(regs)} cards')
            
            # Group by district within type
            district_groups = defaultdict(list)
            for reg in regs:
                district_groups[reg.city].append(reg)
            
            # Sort districts by registration number district code
            def get_district_code(district_name):
                # Get a sample registration from this district to extract district code
                sample_reg = district_groups[district_name][0]
                if sample_reg.registration_number:
                    # Extract district code from registration number (e.g., YCS-MP-AGA-0001 -> AGA)
                    parts = sample_reg.registration_number.split('-')
                    if len(parts) >= 3:
                        return parts[2]  # District code
                return district_name  # Fallback to district name
            
            sorted_districts = sorted(district_groups.keys(), key=get_district_code)
            for district in sorted_districts:
                district_regs = district_groups[district]
                
                self.stdout.write(f'  📍 {district}: {len(district_regs)} cards')
                
                # Check if MP state for upzone grouping
                if district_regs[0].state_code == 'MP':
                    # Group by upzone within district
                    upzone_groups = defaultdict(list)
                    for reg in district_regs:
                        # Reset DB connection to prevent timeout
                        connection.ensure_connection()
                        try:
                            upzone = reg.get_upzone_for_district()
                            upzone_name = upzone.name if upzone else 'No_UpZone'
                        except:
                            upzone_name = 'No_UpZone'
                        upzone_groups[upzone_name].append(reg)
                    
                    # Sort upzones by registration number sequence
                    def get_upzone_sort_key(upzone_name):
                        # Get first registration number from this upzone for sorting
                        sample_reg = upzone_groups[upzone_name][0]
                        if sample_reg.registration_number:
                            # Extract serial number for sorting (e.g., YCS-MP-AGA-0001 -> 0001)
                            parts = sample_reg.registration_number.split('-')
                            if len(parts) >= 4:
                                try:
                                    return int(parts[3])  # Serial number
                                except ValueError:
                                    pass
                        return upzone_name  # Fallback
                    
                    sorted_upzones = sorted(upzone_groups.keys(), key=get_upzone_sort_key)
                    for upzone_name in sorted_upzones:
                        upzone_regs = upzone_groups[upzone_name]
                        self.stdout.write(f'    🏢 {upzone_name}: {len(upzone_regs)} cards')
                        
                        # Sort registrations within upzone by registration number
                        sorted_upzone_regs = sorted(upzone_regs, key=lambda r: r.registration_number or f'ZZZ{r.id}')
                        # Process upzone in batches with single Chrome instance
                        connection.close()  # Close DB connection before batch processing
                        batch_results = self.generate_cards_batch(sorted_upzone_regs, type_path, district, upzone_name)
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
                    # Non-MP states - direct to type folder, sorted by registration number
                    sorted_district_regs = sorted(district_regs, key=lambda r: r.registration_number or f'ZZZ{r.id}')
                    # Process district in batches
                    connection.close()  # Close DB connection before batch processing
                    batch_results = self.generate_cards_batch(sorted_district_regs, type_path, district)
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
        self.stdout.write(f'✅ Successfully exported: {total_exported} cards')
        self.stdout.write(f'❌ Failed: {total_failed} cards')
        self.stdout.write(f'📁 Location: {os.path.abspath(output_dir)}')

    def generate_cards_batch(self, registrations, type_path, district, upzone_name=None):
        """Generate multiple cards with single Chrome instance"""
        results = []
        driver = None
        
        try:
            # Setup Chrome once for batch
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_window_size(900, 1400)
            
            for reg in registrations:
                try:
                    if upzone_name:
                        filename = f"{district}_{upzone_name}_{reg.id}_{reg.registration_number or 'NO_REG'}_{reg.full_name.replace(' ', '_')}.jpg"
                    else:
                        filename = f"{district}_{reg.id}_{reg.registration_number or 'NO_REG'}_{reg.full_name.replace(' ', '_')}.jpg"
                    
                    filepath = os.path.join(type_path, filename)
                    
                    # Skip if file already exists
                    if os.path.exists(filepath):
                        results.append((True, f"SKIPPED: {filename}"))
                        continue
                    
                    if self.generate_single_card(reg, filepath, driver):
                        results.append((True, filename))
                    else:
                        results.append((False, filename))
                except Exception as e:
                    results.append((False, f"Error: {str(e)}"))
                    
        except Exception as e:
            # Fallback to individual generation
            for reg in registrations:
                if upzone_name:
                    filename = f"{district}_{upzone_name}_{reg.id}_{reg.registration_number or 'NO_REG'}_{reg.full_name.replace(' ', '_')}.jpg"
                else:
                    filename = f"{district}_{reg.id}_{reg.registration_number or 'NO_REG'}_{reg.full_name.replace(' ', '_')}.jpg"
                filepath = os.path.join(type_path, filename)
                
                # Skip if file already exists
                if os.path.exists(filepath):
                    results.append((True, f"SKIPPED: {filename}"))
                else:
                    results.append((self.generate_card(reg, filepath), filename))
        finally:
            if driver:
                driver.quit()
                
        return results
    
    def generate_single_card(self, registration, output_path, driver):
        """Generate single card with existing driver"""
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
            
            # Temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_html = f.name
            
            try:
                file_url = f'file:///{temp_html.replace(chr(92), "/")}' if os.name == 'nt' else f'file://{temp_html}'
                driver.get(file_url)
                time.sleep(0.5)  # Reduced wait time
                
                screenshot = driver.get_screenshot_as_png()
                
                img = Image.open(io.BytesIO(screenshot))
                if img.height < 1240:
                    new_img = Image.new('RGB', (833, 1240), 'white')
                    new_img.paste(img, (0, 0))
                    cropped_img = new_img
                else:
                    cropped_img = img.crop((0, 0, 833, 1240))
                
                cropped_img = cropped_img.convert('RGB')
                cropped_img.save(output_path, 'JPEG', quality=95)
                
                return True
                
            finally:
                if os.path.exists(temp_html):
                    os.unlink(temp_html)
                    
        except Exception as e:
            return False
    
    def generate_card(self, registration, output_path):
        """Generate single ID card"""
        try:
            # Fallback method for individual card generation
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
                # Setup Chrome options to run completely silently
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-plugins')
                chrome_options.add_argument('--disable-javascript')
                chrome_options.add_argument('--disable-web-security')
                chrome_options.add_argument('--disable-features=VizDisplayCompositor')
                chrome_options.add_argument('--disable-logging')
                chrome_options.add_argument('--disable-dev-tools')
                chrome_options.add_argument('--silent')
                chrome_options.add_argument('--log-level=3')
                chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # Try to find ChromeDriver
                try:
                    driver = webdriver.Chrome(options=chrome_options)

                except Exception as e:
                    try:
                        from selenium.webdriver.chrome.service import Service
                        service = Service('/usr/local/bin/chromedriver')
                        driver = webdriver.Chrome(service=service, options=chrome_options)

                    except Exception as e2:
                        # self.stdout.write(self.style.ERROR(f'Chrome driver failed: {str(e2)}'))
                        return False
                
                driver.set_window_size(900, 1400)
                
                # Use proper file URL format
                file_url = f'file://{temp_html.replace(chr(92), "/")}' if os.name == 'nt' else f'file://{temp_html}'
                driver.get(file_url)
                
                # Wait for page to load
                time.sleep(1)
                
                # Take screenshot and crop to exact size
                screenshot = driver.get_screenshot_as_png()
                driver.quit()
                
                # Crop to exact ID card dimensions (833x1240)
                img = Image.open(io.BytesIO(screenshot))
                if img.height < 1240:
                    new_img = Image.new('RGB', (833, 1240), 'white')
                    new_img.paste(img, (0, 0))
                    cropped_img = new_img
                else:
                    cropped_img = img.crop((0, 0, 833, 1240))
                
                # Convert to JPEG
                cropped_img = cropped_img.convert('RGB')
                cropped_img.save(output_path, 'JPEG', quality=95)
                
                return True
                
            finally:
                for temp_file in [temp_html, temp_png]:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating card: {str(e)}'))
            return False