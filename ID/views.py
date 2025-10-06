from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import render_to_string
from PIL import Image
import qrcode
import io
import os
import base64
import tempfile
import logging
from events.models import EventRegistration
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)

def generate_id_card(request, registration_id):
    """Generate ID card using HTML-to-image conversion for perfect Hindi rendering"""
    registration = get_object_or_404(EventRegistration, id=registration_id)
    
    # Validate DOB for security
    provided_dob = request.GET.get('dob')
    if provided_dob:
        try:
            from datetime import datetime
            if '/' in provided_dob:
                day, month, year = provided_dob.split('/')
                provided_date = datetime(int(year), int(month), int(day)).date()
            else:
                provided_date = datetime.strptime(provided_dob, '%Y-%m-%d').date()
            
            if provided_date != registration.date_of_birth:
                return HttpResponse(
                    "Invalid date of birth verification. Access denied.",
                    status=403,
                    content_type='text/plain'
                )
        except (ValueError, AttributeError):
            return HttpResponse(
                "Invalid date format for verification.",
                status=400,
                content_type='text/plain'
            )
    
    # Check if Chrome/ChromeDriver is available
    try:
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        # Test if ChromeDriver is accessible
        test_options = Options()
        test_options.add_argument('--headless')
        test_options.add_argument('--no-sandbox')
        test_driver = webdriver.Chrome(options=test_options)
        test_driver.quit()
    except Exception as e:
        # Return error response if Chrome is not available
        return HttpResponse(
            f"ID card generation service is temporarily unavailable. "
            f"Chrome/ChromeDriver not found: {str(e)}",
            status=503,
            content_type='text/plain'
        )
    
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
    
    try:
        # Setup Chrome options for deployment
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--hide-scrollbars')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--force-device-scale-factor=1')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-javascript')
        chrome_options.add_argument('--virtual-time-budget=5000')
        
        # Try to find ChromeDriver in common locations
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            # Try with explicit path
            try:
                driver = webdriver.Chrome('/usr/local/bin/chromedriver', options=chrome_options)
            except Exception as e2:
                raise Exception(f"ChromeDriver not found. Install Chrome and ChromeDriver: {str(e2)}")
        driver.set_window_size(900, 1400)  # Much larger height
        driver.execute_script("document.body.style.zoom='1.0'")
        # Use proper file URL format for both Windows and Linux
        file_url = f'file://{temp_html_path.replace(chr(92), "/")}' if os.name == 'nt' else f'file://{temp_html_path}'
        driver.get(file_url)
        
        # Wait for page to load completely
        import time
        time.sleep(1)
        
        # Take screenshot and crop to exact size
        screenshot = driver.get_screenshot_as_png()
        driver.quit()
        
        # Crop to exact ID card dimensions (833x1240)
        img = Image.open(io.BytesIO(screenshot))
        # Ensure we have enough image to crop
        if img.height < 1240:
            # Create new image with white background if screenshot is too small
            new_img = Image.new('RGB', (833, 1240), 'white')
            new_img.paste(img, (0, 0))
            cropped_img = new_img
        else:
            cropped_img = img.crop((0, 0, 833, 1240))
        
        # Convert back to bytes
        buffer = io.BytesIO()
        cropped_img.save(buffer, format='PNG')
        png_bytes = buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Error generating ID card for registration {registration_id}: {str(e)}")
        raise e
    finally:
        # Clean up temp file
        if os.path.exists(temp_html_path):
            os.unlink(temp_html_path)
    
    logger.info(f"Successfully generated ID card for registration {registration_id}")
    
    # Convert format if needed
    format_type = request.GET.get('format', 'PNG').upper()
    if format_type == 'JPG' or format_type == 'JPEG':
        # Convert PNG to JPEG
        img = Image.open(io.BytesIO(png_bytes))
        img = img.convert('RGB')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        image_bytes = buffer.getvalue()
        content_type = 'image/jpeg'
        format_type = 'jpg'
    else:
        image_bytes = png_bytes
        content_type = 'image/png'
        format_type = 'png'
    
    response = HttpResponse(image_bytes, content_type=content_type)
    filename = f"id_card_{registration.registration_number or registration.id}.{format_type}"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response