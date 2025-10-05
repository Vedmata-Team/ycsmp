#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

def debug_vehicle_pass_paths():
    """Debug vehicle pass background image paths and files"""
    
    print("=== VEHICLE PASS DEBUG ANALYSIS ===\n")
    
    # Check Django settings
    print("1. DJANGO SETTINGS:")
    print(f"   STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'Not set')}")
    print(f"   STATICFILES_DIRS: {getattr(settings, 'STATICFILES_DIRS', 'Not set')}")
    print(f"   BASE_DIR: {getattr(settings, 'BASE_DIR', 'Not set')}")
    print(f"   DEBUG: {getattr(settings, 'DEBUG', 'Not set')}")
    
    # Determine static directories to check
    static_dirs = []
    if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
        static_dirs.append(settings.STATIC_ROOT)
    if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
        static_dirs.extend(settings.STATICFILES_DIRS)
    
    print(f"\n2. STATIC DIRECTORIES TO CHECK: {len(static_dirs)}")
    for i, static_dir in enumerate(static_dirs, 1):
        print(f"   {i}. {static_dir}")
    
    # Check each static directory
    for i, static_dir in enumerate(static_dirs, 1):
        print(f"\n3.{i} CHECKING STATIC DIR: {static_dir}")
        print(f"     Directory exists: {os.path.exists(static_dir)}")
        print(f"     Directory readable: {os.access(static_dir, os.R_OK) if os.path.exists(static_dir) else False}")
        print(f"     Directory writable: {os.access(static_dir, os.W_OK) if os.path.exists(static_dir) else False}")
        
        if os.path.exists(static_dir):
            try:
                contents = os.listdir(static_dir)
                print(f"     Contents ({len(contents)} items): {contents[:10]}{'...' if len(contents) > 10 else ''}")
            except PermissionError:
                print("     ERROR: Permission denied to list directory contents")
        
        # Check Vehicle_Pass subdirectory
        vehicle_pass_dir = os.path.join(static_dir, 'Vehicle_Pass')
        print(f"\n     Vehicle_Pass Directory: {vehicle_pass_dir}")
        print(f"     Vehicle_Pass exists: {os.path.exists(vehicle_pass_dir)}")
        
        if os.path.exists(vehicle_pass_dir):
            try:
                vp_contents = os.listdir(vehicle_pass_dir)
                print(f"     Vehicle_Pass contents: {vp_contents}")
                
                # Check specific background files
                required_files = ['volunteer.png', 'org_member.png', 'participant.png']
                print(f"\n     BACKGROUND FILES CHECK:")
                for filename in required_files:
                    filepath = os.path.join(vehicle_pass_dir, filename)
                    exists = os.path.exists(filepath)
                    readable = os.access(filepath, os.R_OK) if exists else False
                    size = os.path.getsize(filepath) if exists else 0
                    
                    print(f"       {filename}:")
                    print(f"         Path: {filepath}")
                    print(f"         Exists: {exists}")
                    print(f"         Readable: {readable}")
                    print(f"         Size: {size} bytes")
                    
                    if exists and readable:
                        try:
                            with open(filepath, 'rb') as f:
                                data = f.read(100)  # Read first 100 bytes
                                print(f"         File header: {data[:20].hex()}")
                                print(f"         Is PNG: {data.startswith(b'\\x89PNG')}")
                        except Exception as e:
                            print(f"         Read error: {e}")
                            
            except PermissionError:
                print("     ERROR: Permission denied to list Vehicle_Pass directory")
        else:
            print("     Vehicle_Pass directory does not exist")
            print(f"     Attempting to create: {vehicle_pass_dir}")
            try:
                os.makedirs(vehicle_pass_dir, exist_ok=True)
                print("     ✓ Vehicle_Pass directory created successfully")
            except Exception as e:
                print(f"     ✗ Failed to create directory: {e}")

def create_sample_images():
    """Create sample background images for testing"""
    try:
        from PIL import Image
        
        # Get first available static directory
        static_dirs = []
        if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
            static_dirs.append(settings.STATIC_ROOT)
        if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
            static_dirs.extend(settings.STATICFILES_DIRS)
        
        if not static_dirs:
            print("\n4. SAMPLE IMAGE CREATION: No static directories available")
            return
        
        static_dir = static_dirs[0]
        vehicle_pass_dir = os.path.join(static_dir, 'Vehicle_Pass')
        
        print(f"\n4. CREATING SAMPLE IMAGES IN: {vehicle_pass_dir}")
        
        # Create directory if it doesn't exist
        os.makedirs(vehicle_pass_dir, exist_ok=True)
        
        # Image dimensions (10cm x 5cm at 300 DPI)
        width, height = 1134, 567
        
        # Create sample images with different colors
        images = {
            'volunteer.png': '#990000',      # Red for volunteers
            'org_member.png': '#ff9900',     # Orange for organization
            'participant.png': '#0066cc'     # Blue for participants
        }
        
        for filename, bg_color in images.items():
            filepath = os.path.join(vehicle_pass_dir, filename)
            
            # Create image
            img = Image.new('RGB', (width, height), bg_color)
            
            # Add orange header (top 0.9cm ≈ 106 pixels at 300 DPI)
            header_height = int(0.9 * 118)  # 118 pixels per cm
            for y in range(header_height):
                for x in range(width):
                    img.putpixel((x, y), (255, 107, 0))  # Orange color
            
            # Save image
            img.save(filepath, 'PNG')
            size = os.path.getsize(filepath)
            print(f"   ✓ Created {filename} ({size} bytes)")
        
        print("   Sample images created successfully!")
        
    except ImportError:
        print("\n4. SAMPLE IMAGE CREATION: PIL not available, creating placeholder files")
        
        static_dir = static_dirs[0] if static_dirs else None
        if not static_dir:
            return
            
        vehicle_pass_dir = os.path.join(static_dir, 'Vehicle_Pass')
        os.makedirs(vehicle_pass_dir, exist_ok=True)
        
        # Create placeholder files
        for filename in ['volunteer.png', 'org_member.png', 'participant.png']:
            filepath = os.path.join(vehicle_pass_dir, filename)
            with open(filepath, 'w') as f:
                f.write(f"Placeholder for {filename}")
            print(f"   ✓ Created placeholder {filename}")

def test_image_loading():
    """Test the actual image loading process"""
    print("\n5. TESTING IMAGE LOADING PROCESS:")
    
    from events.models import EventRegistration
    
    # Test different registration types
    test_cases = [
        ('volunteer', 'volunteer.png'),
        ('organization_representative', 'org_member.png'),
        ('participant', 'participant.png')
    ]
    
    static_dir = settings.STATIC_ROOT or (settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None)
    
    for reg_type, expected_file in test_cases:
        print(f"\n   Testing {reg_type} -> {expected_file}:")
        
        if static_dir:
            bg_path = os.path.join(static_dir, 'Vehicle_Pass', expected_file)
            print(f"     Expected path: {bg_path}")
            print(f"     File exists: {os.path.exists(bg_path)}")
            
            if os.path.exists(bg_path):
                try:
                    with open(bg_path, 'rb') as f:
                        data = f.read()
                        import base64
                        b64_data = base64.b64encode(data).decode()
                        print(f"     File size: {len(data)} bytes")
                        print(f"     Base64 size: {len(b64_data)} characters")
                        print(f"     Base64 preview: {b64_data[:50]}...")
                except Exception as e:
                    print(f"     Error reading file: {e}")
        else:
            print("     No static directory configured")

if __name__ == "__main__":
    debug_vehicle_pass_paths()
    create_sample_images()
    test_image_loading()
    print("\n=== DEBUG ANALYSIS COMPLETE ===")