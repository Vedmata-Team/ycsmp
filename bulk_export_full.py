#!/usr/bin/env python
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

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
import time

def bulk_export_all_cards():
    """Full export of all approved ID cards with proper folder structure"""
    
    # Base export directory
    base_export_path = "ID_Cards_Export"
    
    # Create base directory
    os.makedirs(base_export_path, exist_ok=True)
    
    # Get all approved registrations
    registrations = EventRegistration.objects.filter(
        approval_status='approved'
    ).select_related('responsibility').order_by('registration_type', 'state', 'city', 'id')
    
    print(f"🚀 Starting bulk export of {registrations.count()} approved ID cards")
    print(f"📁 Export directory: {os.path.abspath(base_export_path)}")
    
    # Group by registration type
    type_groups = defaultdict(list)
    for reg in registrations:
        type_groups[reg.registration_type].append(reg)
    
    total_exported = 0
    total_failed = 0
    
    for reg_type, regs in type_groups.items():
        # Create type folder
        folder_name = {
            'participant': 'Participants',
            'volunteer': 'Volunteers', 
            'organization_representative': 'Organizations'
        }.get(reg_type, reg_type)
        
        type_path = os.path.join(base_export_path, folder_name)
        os.makedirs(type_path, exist_ok=True)
        
        print(f"\n📂 Processing {folder_name}: {len(regs)} cards")
        
        # Group by district
        district_groups = defaultdict(list)
        for reg in regs:
            district_groups[reg.city].append(reg)
        
        for district, district_regs in district_groups.items():
            district_path = os.path.join(type_path, district)
            os.makedirs(district_path, exist_ok=True)
            
            print(f"  📍 {district}: {len(district_regs)} cards")
            
            # Check if MP state for upzone grouping
            if district_regs[0].state_code == 'MP':
                # Group by upzone
                upzone_groups = defaultdict(list)
                for reg in district_regs:
                    upzone = reg.get_upzone_for_district()
                    upzone_name = upzone.name if upzone else 'No_UpZone'
                    upzone_groups[upzone_name].append(reg)
                
                for upzone_name, upzone_regs in upzone_groups.items():
                    upzone_path = os.path.join(district_path, upzone_name)
                    os.makedirs(upzone_path, exist_ok=True)
                    
                    print(f"    🏢 {upzone_name}: {len(upzone_regs)} cards")
                    
                    # Export cards in this upzone
                    for i, reg in enumerate(upzone_regs, 1):
                        try:
                            filename = f"{reg.id}_{reg.registration_number or 'NO_REG'}_{reg.full_name.replace(' ', '_')}.jpg"
                            filepath = os.path.join(upzone_path, filename)
                            
                            if generate_card_image(reg, filepath):
                                print(f"      ✅ {i}/{len(upzone_regs)}: {filename}")
                                total_exported += 1
                            else:
                                print(f"      ❌ {i}/{len(upzone_regs)}: {filename} - FAILED")
                                total_failed += 1
                                
                        except Exception as e:
                            print(f"      ❌ {i}/{len(upzone_regs)}: Error - {str(e)}")
                            total_failed += 1
            else:
                # Non-MP states - direct district export
                for i, reg in enumerate(district_regs, 1):
                    try:
                        filename = f"{reg.id}_{reg.registration_number or 'NO_REG'}_{reg.full_name.replace(' ', '_')}.jpg"
                        filepath = os.path.join(district_path, filename)
                        
                        if generate_card_image(reg, filepath):
                            print(f"    ✅ {i}/{len(district_regs)}: {filename}")
                            total_exported += 1
                        else:
                            print(f"    ❌ {i}/{len(district_regs)}: {filename} - FAILED")
                            total_failed += 1
                            
                    except Exception as e:
                        print(f"    ❌ {i}/{len(district_regs)}: Error - {str(e)}")
                        total_failed += 1
    
    print(f"\n🎉 Export completed!")
    print(f"✅ Successfully exported: {total_exported} cards")
    print(f"❌ Failed: {total_failed} cards")
    print(f"📁 Export location: {os.path.abspath(base_export_path)}")

def generate_card_image(registration, output_path):
    """Generate single ID card image using wkhtmltoimage"""
    try:
        # Generate QR code
        profile_url = f"https://ycsmp.in{registration.get_profile_url()}"
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(profile_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert QR to base64
        buffer = io.BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Get background image
        if registration.registration_type == 'volunteer':
            bg_file = 'Volunteers_ID Card_.png'
        elif registration.registration_type == 'organization_representative':
            bg_file = 'Organization_ID Card_.png'
        else:
            bg_file = 'Participants_ID Card_.png'
        
        bg_path = os.path.join(settings.STATICFILES_DIRS[0], 'ID_Card', bg_file)
        with open(bg_path, 'rb') as f:
            bg_image_base64 = base64.b64encode(f.read()).decode()
        
        # Residence status
        residence_status = "आवंटित" if registration.approval_status == 'approved' else "आवंटित नहीं"
        
        # Render HTML
        html_content = render_to_string('ID/id_card_html.html', {
            'registration': registration,
            'qr_code_base64': qr_code_base64,
            'residence_status': residence_status,
            'bg_image_base64': bg_image_base64,
        })
        
        # Create temp HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_html_path = f.name
        
        # Create temp PNG file
        temp_png_path = temp_html_path.replace('.html', '.png')
        
        try:
            # Use wkhtmltoimage
            cmd = [
                'wkhtmltoimage',
                '--width', '833',
                '--height', '1240',
                '--format', 'png',
                '--quality', '100',
                '--disable-javascript',
                '--no-stop-slow-scripts',
                temp_html_path,
                temp_png_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return False
            
            # Convert PNG to JPG
            img = Image.open(temp_png_path)
            img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=95)
            
            return True
            
        finally:
            # Cleanup temp files
            if os.path.exists(temp_html_path):
                os.unlink(temp_html_path)
            if os.path.exists(temp_png_path):
                os.unlink(temp_png_path)
                
    except Exception as e:
        print(f"      Error generating {registration.full_name}: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 ID Cards Bulk Export - FULL VERSION")
    print("=" * 50)
    
    # Confirm before starting
    response = input("This will export ALL approved ID cards. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Export cancelled.")
        sys.exit(0)
    
    start_time = time.time()
    bulk_export_all_cards()
    end_time = time.time()
    
    print(f"⏱️  Total time: {end_time - start_time:.2f} seconds")