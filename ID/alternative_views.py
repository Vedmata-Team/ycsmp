from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import render_to_string
from PIL import Image
import qrcode
import io
import os
import base64
import tempfile
import subprocess
from events.models import EventRegistration

def generate_id_card_wkhtmltopdf(request, registration_id):
    """Alternative ID card generation using wkhtmltopdf (more deployment-friendly)"""
    registration = get_object_or_404(EventRegistration, id=registration_id)
    
    # Generate QR code
    profile_url = f"https://ycsmp.in{registration.get_profile_url()}"
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(profile_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64
    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Get background image and convert to base64
    if registration.registration_type == 'volunteer':
        bg_file = 'Volunteers_ID Card_.png'
    elif registration.registration_type == 'organization_representative':
        bg_file = 'Organization_ID Card_.png'
    else:
        bg_file = 'Participants_ID Card_.png'
    
    # Load background image as base64
    bg_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'ID_Card', bg_file)
    with open(bg_path, 'rb') as f:
        bg_image_base64 = base64.b64encode(f.read()).decode()
    
    # Residence status
    residence_status = "आवंटित" if registration.approval_status == 'approved' else "आवंटित नहीं"
    
    # Render HTML template
    html_content = render_to_string('ID/id_card_html.html', {
        'registration': registration,
        'qr_code_base64': qr_code_base64,
        'residence_status': residence_status,
        'bg_image_base64': bg_image_base64,
    })
    
    # Create temporary HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        temp_html_path = f.name
    
    # Create temporary image file
    temp_image_path = temp_html_path.replace('.html', '.png')
    
    try:
        # Use wkhtmltoimage to convert HTML to image
        wkhtml_cmd = 'wkhtmltoimage'
        if os.name == 'nt':  # Windows
            wkhtml_cmd = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'
        
        cmd = [
            wkhtml_cmd,
            '--width', '833',
            '--height', '1240',
            '--format', 'png',
            '--quality', '100',
            '--disable-javascript',
            '--no-stop-slow-scripts',
            temp_html_path,
            temp_image_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise Exception(f"wkhtmltoimage failed: {result.stderr}")
        
        # Read the generated image
        with open(temp_image_path, 'rb') as f:
            image_bytes = f.read()
        
    except FileNotFoundError:
        raise Exception("wkhtmltoimage not installed. Please install wkhtmltopdf package.")
    except subprocess.TimeoutExpired:
        raise Exception("Image generation timed out")
    finally:
        # Clean up temp files
        if os.path.exists(temp_html_path):
            os.unlink(temp_html_path)
        if os.path.exists(temp_image_path):
            os.unlink(temp_image_path)
    
    # Convert format if needed
    format_type = request.GET.get('format', 'PNG').upper()
    if format_type == 'JPG' or format_type == 'JPEG':
        # Convert PNG to JPEG
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert('RGB')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        image_bytes = buffer.getvalue()
        content_type = 'image/jpeg'
        format_type = 'jpg'
    else:
        content_type = 'image/png'
        format_type = 'png'
    
    response = HttpResponse(image_bytes, content_type=content_type)
    filename = f"id_card_{registration.registration_number or registration.id}.{format_type}"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response