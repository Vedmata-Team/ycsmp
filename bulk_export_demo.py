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

def demo_bulk_export():
    """Demo version - shows structure and exports first 2 cards per category"""
    
    # Get approved registrations
    registrations = EventRegistration.objects.filter(
        approval_status='approved'
    ).select_related('responsibility').order_by('registration_type', 'state', 'city')
    
    print(f"📊 Total approved registrations: {registrations.count()}")
    
    # Group by registration type
    grouped = defaultdict(list)
    for reg in registrations:
        grouped[reg.registration_type].append(reg)
    
    # Show structure
    print("\n📁 Folder Structure Preview:")
    base_path = "ID_Cards_Export"
    
    for reg_type, regs in grouped.items():
        folder_name = {
            'participant': 'Participants',
            'volunteer': 'Volunteers', 
            'organization_representative': 'Organizations'
        }.get(reg_type, reg_type)
        
        print(f"├── {folder_name}/ ({len(regs)} cards)")
        
        # Group by district for demo
        district_groups = defaultdict(list)
        for reg in regs[:6]:  # Demo: first 6 only
            district_groups[reg.city].append(reg)
        
        for district, district_regs in district_groups.items():
            print(f"│   ├── {district}/ ({len(district_regs)} cards)")
            
            # Group by upzone if MP
            if district_regs[0].state_code == 'MP':
                upzone_groups = defaultdict(list)
                for reg in district_regs:
                    upzone = reg.get_upzone_for_district()
                    upzone_name = upzone.name if upzone else 'No_UpZone'
                    upzone_groups[upzone_name].append(reg)
                
                for upzone, upzone_regs in upzone_groups.items():
                    print(f"│   │   ├── {upzone}/ ({len(upzone_regs)} cards)")
                    for reg in upzone_regs[:2]:  # Demo: 2 per upzone
                        filename = f"{reg.id}_{reg.registration_number or 'NO_REG'}_{reg.full_name.replace(' ', '_')}.jpg"
                        print(f"│   │   │   └── {filename}")
            else:
                for reg in district_regs[:2]:  # Demo: 2 per district
                    filename = f"{reg.id}_{reg.registration_number or 'NO_REG'}_{reg.full_name.replace(' ', '_')}.jpg"
                    print(f"│   │   └── {filename}")
    
    print(f"\n🎯 Demo Export Process:")
    
    # Demo: Export first card from each type
    demo_exports = []
    for reg_type, regs in grouped.items():
        if regs:
            demo_exports.append(regs[0])
    
    print(f"📤 Exporting {len(demo_exports)} demo cards...")
    
    for i, reg in enumerate(demo_exports, 1):
        try:
            print(f"  {i}. Generating: {reg.full_name} ({reg.get_registration_type_display()})")
            
            # Generate card (simplified for demo)
            success = generate_single_card_demo(reg)
            
            if success:
                print(f"     ✅ Generated successfully")
            else:
                print(f"     ❌ Generation failed")
                
        except Exception as e:
            print(f"     ❌ Error: {str(e)}")
    
    print(f"\n✨ Demo completed! Ready for full export?")

def generate_single_card_demo(registration):
    """Demo card generation - simplified version"""
    try:
        # Check if wkhtmltoimage is available
        result = subprocess.run(['wkhtmltoimage', '--version'], 
                              capture_output=True, timeout=5)
        if result.returncode != 0:
            print("     ⚠️  wkhtmltoimage not found - would use fallback")
            return False
        
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
        
        # Render HTML (demo - just check template exists)
        html_content = render_to_string('ID/id_card_html.html', {
            'registration': registration,
            'qr_code_base64': qr_code_base64,
            'residence_status': residence_status,
            'bg_image_base64': bg_image_base64,
        })
        
        print(f"     📄 HTML template rendered ({len(html_content)} chars)")
        return True
        
    except Exception as e:
        print(f"     ❌ Demo generation error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 ID Cards Bulk Export - DEMO VERSION")
    print("=" * 50)
    demo_bulk_export()