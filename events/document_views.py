from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import os
import json
from django.utils.text import slugify
from datetime import datetime

@require_http_methods(["POST"])
def upload_document(request):
    """Handle document upload with compression and proper naming"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No file provided'})
        
        file = request.FILES['file']
        field_name = request.POST.get('field_name')
        
        if not field_name:
            return JsonResponse({'success': False, 'error': 'Field name not provided'})
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            return JsonResponse({'success': False, 'error': 'Only image files are allowed'})
        
        # Validate file size (max 5MB before compression)
        if file.size > 5 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'File too large. Maximum 5MB allowed'})
        
        # Get user info from form data or session
        user_name = request.POST.get('user_name') or request.session.get('temp_user_name', 'user')
        user_id = request.POST.get('user_id') or request.session.get('temp_user_id', datetime.now().strftime('%Y%m%d%H%M%S'))
        
        # Store in session for future uploads
        request.session['temp_user_name'] = user_name
        request.session['temp_user_id'] = user_id
        
        # Process and save file
        file_url = process_and_save_document(file, field_name, user_name, user_id)
        
        if file_url:
            return JsonResponse({'success': True, 'file_url': file_url})
        else:
            return JsonResponse({'success': False, 'error': 'Failed to process file'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def process_and_save_document(file, field_name, user_name, user_id):
    """Process image and save with proper naming and folder structure"""
    try:
        # Open image with PIL
        image = Image.open(file)
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Compress image to target size (200KB)
        compressed_image = compress_image_to_size(image, max_size_kb=200)
        
        # Generate proper file path
        file_path = generate_document_path(field_name, user_name, user_id)
        
        # Save compressed image
        saved_path = default_storage.save(file_path, ContentFile(compressed_image))
        
        # Return URL
        return default_storage.url(saved_path)
        
    except Exception as e:
        print(f"Error processing document: {e}")
        return None

def compress_image_to_size(image, max_size_kb=200):
    """Compress image to specified size in KB"""
    import io
    
    # Start with high quality
    quality = 95
    max_size_bytes = max_size_kb * 1024
    
    while quality > 10:
        # Create a BytesIO object to hold the image data
        img_io = io.BytesIO()
        
        # Save image with current quality
        image.save(img_io, format='JPEG', quality=quality, optimize=True)
        
        # Check size
        img_size = img_io.tell()
        
        if img_size <= max_size_bytes:
            img_io.seek(0)
            return img_io.getvalue()
        
        # Reduce quality for next iteration
        quality -= 5
    
    # If still too large, resize image
    img_io = io.BytesIO()
    
    # Calculate new dimensions (reduce by 10% each time)
    width, height = image.size
    new_width = int(width * 0.9)
    new_height = int(height * 0.9)
    
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    resized_image.save(img_io, format='JPEG', quality=85, optimize=True)
    
    img_io.seek(0)
    return img_io.getvalue()

def generate_document_path(field_name, user_name, user_id):
    """Generate organized file path for documents"""
    # Create safe filename components
    safe_name = slugify(user_name)[:20]  # Limit length
    
    # Get current date for folder organization
    now = datetime.now()
    year = now.year
    month = f"{now.month:02d}"
    
    # Map field names to document types
    doc_type_map = {
        'aadhar_full': 'aadhar_full',
        'aadhar_front': 'aadhar_front', 
        'aadhar_back': 'aadhar_back',
        'passport_photo': 'passport'
    }
    
    doc_type = doc_type_map.get(field_name, field_name)
    
    # Create folder structure: documents/year/month/
    folder_path = f"documents/{year}/{month}"
    
    # Create filename: Name_ID_DocType.jpg
    filename = f"{safe_name}_{user_id}_{doc_type}.jpg"
    
    return os.path.join(folder_path, filename)

@require_http_methods(["POST"])
def store_temp_user_info(request):
    """Store temporary user info in session for file naming"""
    try:
        data = json.loads(request.body)
        request.session['temp_user_name'] = data.get('name', 'user')
        request.session['temp_user_id'] = data.get('id', datetime.now().strftime('%Y%m%d%H%M%S'))
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})