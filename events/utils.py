from PIL import Image
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

def compress_image(image_file, max_size_kb=240, quality=85):
    """
    Compress image to specified size in KB
    """
    # Open image
    img = Image.open(image_file)
    
    # Convert to RGB if necessary
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # Get original format
    format = img.format or 'JPEG'
    if format.upper() not in ['JPEG', 'PNG', 'WEBP']:
        format = 'JPEG'
    
    # Start with original quality
    current_quality = quality
    
    while current_quality > 10:
        # Create a BytesIO object
        output = io.BytesIO()
        
        # Save image with current quality
        img.save(output, format=format, quality=current_quality, optimize=True)
        
        # Check size
        size_kb = output.tell() / 1024
        
        if size_kb <= max_size_kb:
            break
            
        # Reduce quality for next iteration
        current_quality -= 5
        output.seek(0)
        output.truncate(0)
    
    # If still too large, resize image
    if size_kb > max_size_kb:
        # Calculate new dimensions (reduce by 10% each iteration)
        width, height = img.size
        while size_kb > max_size_kb and width > 100 and height > 100:
            width = int(width * 0.9)
            height = int(height * 0.9)
            
            # Resize image
            resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Save with current quality
            output = io.BytesIO()
            resized_img.save(output, format=format, quality=current_quality, optimize=True)
            size_kb = output.tell() / 1024
    
    # Reset file pointer
    output.seek(0)
    
    # Create new InMemoryUploadedFile
    return InMemoryUploadedFile(
        output, 'ImageField', 
        f"{image_file.name.split('.')[0]}.{format.lower()}", 
        f'image/{format.lower()}',
        sys.getsizeof(output), None
    )

def compress_banner_image(image_file):
    """
    Compress banner image to 350KB
    """
    return compress_image(image_file, max_size_kb=350, quality=90)

def compress_regular_image(image_file):
    """
    Compress regular image to 240KB
    """
    return compress_image(image_file, max_size_kb=240, quality=85)