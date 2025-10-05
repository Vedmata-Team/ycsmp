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
import subprocess

logger = logging.getLogger(__name__)

def get_primary_vehicle_user(vehicle_number):
    """Get primary user for a vehicle based on priority rules"""
    # Get all registrations with this vehicle number
    registrations = EventRegistration.objects.filter(
        vehicle_number=vehicle_number,
        approval_status__in=['district_approved', 'upzone_approved', 'approved']
    ).select_related('responsibility')
    
    if not registrations.exists():
        return None
    
    if registrations.count() == 1:
        return registrations.first()
    
    # Priority 1: Registration type (organization > volunteer > participant)
    type_priority = {
        'organization_representative': 1,
        'volunteer': 2, 
        'participant': 3
    }
    
    # Sort by registration type priority
    by_type = sorted(registrations, key=lambda r: type_priority.get(r.registration_type, 4))
    
    # Check if top priority type is unique
    top_type = by_type[0].registration_type
    same_type = [r for r in by_type if r.registration_type == top_type]
    
    if len(same_type) == 1:
        return same_type[0]
    
    # Priority 2: Gender (Male > Female)
    gender_priority = {'M': 1, 'F': 2, 'O': 3}
    by_gender = sorted(same_type, key=lambda r: gender_priority.get(r.gender, 4))
    
    # Check if top gender is unique
    top_gender = by_gender[0].gender
    same_gender = [r for r in by_gender if r.gender == top_gender]
    
    if len(same_gender) == 1:
        return same_gender[0]
    
    # Priority 3: Date of birth (older person gets priority)
    by_age = sorted(same_gender, key=lambda r: r.date_of_birth)
    
    return by_age[0]

def generate_vehicle_pass(request, registration_id, vehicle_number):
    """Generate Vehicle Pass using HTML-to-image conversion for perfect Hindi rendering"""
    registration = get_object_or_404(EventRegistration, id=registration_id)
    
    # Validate vehicle number matches registration
    if registration.vehicle_number != vehicle_number:
        return HttpResponse(
            "Vehicle number mismatch. Invalid access.",
            status=400,
            content_type='text/plain'
        )
    
    # Check for vehicle number conflicts and resolve priority
    primary_user = get_primary_vehicle_user(vehicle_number)
    if primary_user and primary_user.id != registration.id:
        return HttpResponse(
            f"Vehicle pass can only be generated for primary user: {primary_user.full_name}. Contact admin for assistance.",
            status=403,
            content_type='text/plain'
        )
    
    # Check if user has vehicle information
    if not registration.transport_mode or not registration.vehicle_number:
        return HttpResponse(
            "Vehicle information not available for this registration.",
            status=400,
            content_type='text/plain'
        )
    
    # Generate QR code for vehicle verification with vehicle number
    vehicle_verify_url = f"https://ycsmp.in/vehicle-pass/verify/{registration.id}/{vehicle_number}/"
    qr = qrcode.QRCode(version=1, box_size=12, border=3)  # Scaled up 3x
    qr.add_data(vehicle_verify_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64
    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
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
    
    # Load background image as base64
    static_dir = settings.STATIC_ROOT or (settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None)
    bg_path = os.path.join(static_dir, 'Vehicle_Pass', bg_file) if static_dir else None
    
    logger.info(f"DEBUG: Registration type: {registration.registration_type}")
    logger.info(f"DEBUG: Background file: {bg_file}")
    logger.info(f"DEBUG: Static dir: {static_dir}")
    logger.info(f"DEBUG: Background path: {bg_path}")
    logger.info(f"DEBUG: Path exists: {os.path.exists(bg_path) if bg_path else False}")
    
    try:
        if bg_path and os.path.exists(bg_path):
            with open(bg_path, 'rb') as f:
                bg_image_base64 = base64.b64encode(f.read()).decode()
                logger.info(f"DEBUG: Background image loaded successfully, size: {len(bg_image_base64)} chars")
        else:
            bg_image_base64 = ""
            logger.warning(f"DEBUG: Background image not found at: {bg_path}")
    except Exception as e:
        bg_image_base64 = ""
        logger.error(f"DEBUG: Error loading background image: {str(e)}")
    
    # Render HTML template
    html_content = render_to_string('vehicle_pass/vehicle_pass_html.html', {
        'registration': registration,
        'qr_code_base64': qr_code_base64,
        'user_type_hindi': user_type_hindi,
        'bg_image_base64': bg_image_base64,
        'validity_date': '29 अक्टूबर 2025',
    })
    
    # Create temporary HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        temp_html_path = f.name
    
    # Create temporary image file
    temp_image_path = temp_html_path.replace('.html', '.png')
    
    try:
        # Use wkhtmltoimage (same as ID card generation)
        wkhtml_paths = ['wkhtmltoimage', '/usr/bin/wkhtmltoimage', '/usr/local/bin/wkhtmltoimage']
        wkhtml_cmd = 'wkhtmltoimage'
        
        for path in wkhtml_paths:
            try:
                subprocess.run([path, '--version'], capture_output=True, timeout=2)
                wkhtml_cmd = path
                break
            except:
                continue
        
        cmd = [
            wkhtml_cmd,
            '--width', '1181',   # Exact final width
            '--height', '591',   # Exact final height
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
        
        # Read and resize to exact dimensions (like ID cards)
        with open(temp_image_path, 'rb') as f:
            image_bytes = f.read()
        
        # Apply exact ID card cropping logic
        img = Image.open(io.BytesIO(image_bytes))
        
        # Ensure we have enough image to crop (like ID cards)
        if img.height < 591:
            # Create new image with white background if screenshot is too small
            new_img = Image.new('RGB', (1181, 591), 'white')
            new_img.paste(img, (0, 0))
            cropped_img = new_img
        else:
            # Crop to exact vehicle pass dimensions (1181x591)
            cropped_img = img.crop((0, 0, 1181, 591))
        
        # Convert back to bytes (same as ID cards)
        buffer = io.BytesIO()
        cropped_img.save(buffer, format='PNG')
        png_bytes = buffer.getvalue()
        
    except FileNotFoundError:
        raise Exception("wkhtmltoimage not installed. Please install wkhtmltopdf package.")
    except subprocess.TimeoutExpired:
        raise Exception("Vehicle pass generation timed out")
        
    except Exception as e:
        logger.error(f"Error generating vehicle pass for registration {registration_id}: {str(e)}")
        return HttpResponse(f"Vehicle pass generation failed: {str(e)}", status=500)
    finally:
        if os.path.exists(temp_html_path):
            os.unlink(temp_html_path)
        if os.path.exists(temp_image_path):
            os.unlink(temp_image_path)
    
    logger.info(f"Successfully generated vehicle pass for registration {registration_id}")
    
    response = HttpResponse(png_bytes, content_type='image/png')
    filename = f"vehicle_pass_{registration.registration_number or registration.id}.png"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

def vehicle_verify(request, registration_id, vehicle_number):
    """Vehicle verification page accessed via QR code"""
    registration = get_object_or_404(EventRegistration, id=registration_id)
    
    # Validate vehicle number matches registration
    if registration.vehicle_number != vehicle_number:
        return HttpResponse(
            "Vehicle number mismatch. Access denied.",
            status=400,
            content_type='text/plain'
        )
    
    # Check if this is the primary user for this vehicle
    primary_user = get_primary_vehicle_user(vehicle_number)
    is_primary = primary_user and primary_user.id == registration.id
    
    # Get all users with same vehicle for display
    all_vehicle_users = EventRegistration.objects.filter(
        vehicle_number=vehicle_number,
        approval_status__in=['district_approved', 'upzone_approved', 'approved']
    ).exclude(id=registration.id)
    
    context = {
        'registration': registration,
        'profile_url': registration.get_profile_url(),
        'is_primary_user': is_primary,
        'other_vehicle_users': all_vehicle_users,
        'primary_user': primary_user,
    }
    
    return render(request, 'vehicle_pass/vehicle_verify.html', context)

def vehicle_pass_preview(request, registration_id, vehicle_number):
    """Vehicle pass preview page for online viewing"""
    registration = get_object_or_404(EventRegistration, id=registration_id)
    
    # Validate vehicle number matches registration
    if registration.vehicle_number != vehicle_number:
        return HttpResponse(
            "Vehicle number mismatch. Access denied.",
            status=400,
            content_type='text/plain'
        )
    
    # Check if user has vehicle information
    if not registration.transport_mode or not registration.vehicle_number:
        return HttpResponse(
            "Vehicle information not available for this registration.",
            status=400,
            content_type='text/plain'
        )
    
    # Check priority for vehicle conflicts
    primary_user = get_primary_vehicle_user(vehicle_number)
    if primary_user and primary_user.id != registration.id:
        return HttpResponse(
            f"Vehicle pass preview only available for primary user: {primary_user.full_name}.",
            status=403,
            content_type='text/plain'
        )
    
    # Generate QR code for vehicle verification
    vehicle_verify_url = f"https://ycsmp.in/vehicle-pass/verify/{registration.id}/{vehicle_number}/"
    qr = qrcode.QRCode(version=1, box_size=12, border=3)  # Scaled up 3x
    qr.add_data(vehicle_verify_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64
    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
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
    
    # Load background image as base64
    static_dir = settings.STATIC_ROOT or (settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None)
    bg_path = os.path.join(static_dir, 'Vehicle_Pass', bg_file) if static_dir else None
    
    logger.info(f"DEBUG PREVIEW: Registration type: {registration.registration_type}")
    logger.info(f"DEBUG PREVIEW: Background file: {bg_file}")
    logger.info(f"DEBUG PREVIEW: Static dir: {static_dir}")
    logger.info(f"DEBUG PREVIEW: Background path: {bg_path}")
    logger.info(f"DEBUG PREVIEW: Path exists: {os.path.exists(bg_path) if bg_path else False}")
    
    try:
        if bg_path and os.path.exists(bg_path):
            with open(bg_path, 'rb') as f:
                bg_image_base64 = base64.b64encode(f.read()).decode()
                logger.info(f"DEBUG PREVIEW: Background image loaded successfully, size: {len(bg_image_base64)} chars")
        else:
            bg_image_base64 = ""
            logger.warning(f"DEBUG PREVIEW: Background image not found at: {bg_path}")
    except Exception as e:
        bg_image_base64 = ""
        logger.error(f"DEBUG PREVIEW: Error loading background image: {str(e)}")
    
    context = {
        'registration': registration,
        'qr_code_base64': qr_code_base64,
        'user_type_hindi': user_type_hindi,
        'bg_image_base64': bg_image_base64,
        'validity_date': '29 अक्टूबर 2025',
        'download_url': f'/vehicle-pass/generate/{registration.id}/{vehicle_number}/',
        'qr_url': vehicle_verify_url,
    }
    
    return render(request, 'vehicle_pass/vehicle_pass_preview.html', context)