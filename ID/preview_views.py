from django.shortcuts import render, get_object_or_404
from events.models import EventRegistration
import qrcode
import io
import base64

def preview_id_card(request, registration_id):
    """Preview ID card before download"""
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
    
    # Get background image based on registration type
    if registration.registration_type == 'volunteer':
        bg_image = 'ID_Card/Volunteers_ID Card_.png'
    elif registration.registration_type == 'organization_representative':
        bg_image = 'ID_Card/Organization_ID Card_.png'
    else:
        bg_image = 'ID_Card/Participants_ID Card_.png'
    
    residence_status = "आवंटित" if registration.approval_status == 'approved' else "आवंटित नहीं"
    
    context = {
        'registration': registration,
        'bg_image': bg_image,
        'residence_status': residence_status,
        'qr_code_base64': qr_code_base64,
        'download_png_url': f'/id/card/{registration_id}/?format=PNG',
        'download_jpg_url': f'/id/card/{registration_id}/?format=JPG',
    }
    
    return render(request, 'ID/preview_card.html', context)