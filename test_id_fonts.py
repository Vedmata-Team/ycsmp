import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from PIL import Image, ImageFont, ImageDraw

# Test font loading
base_dir = settings.BASE_DIR
fonts_dir = os.path.join(base_dir, "static", "fonts")

print("Testing Poppins font loading...")

try:
    font_bold = ImageFont.truetype(os.path.join(fonts_dir, "Poppins-Bold.ttf"), 48)
    print("✓ Poppins-Bold.ttf loaded successfully")
except Exception as e:
    print(f"✗ Failed to load Poppins-Bold.ttf: {e}")

try:
    font_medium = ImageFont.truetype(os.path.join(fonts_dir, "Poppins-Medium.ttf"), 36)
    print("✓ Poppins-Medium.ttf loaded successfully")
except Exception as e:
    print(f"✗ Failed to load Poppins-Medium.ttf: {e}")

try:
    font_regular = ImageFont.truetype(os.path.join(fonts_dir, "Poppins-Regular.ttf"), 32)
    print("✓ Poppins-Regular.ttf loaded successfully")
except Exception as e:
    print(f"✗ Failed to load Poppins-Regular.ttf: {e}")

# Test Hindi text rendering
print("\nTesting Hindi text rendering...")
test_img = Image.new('RGB', (400, 200), 'white')
draw = ImageDraw.Draw(test_img)

hindi_text = "पंजीकरण संख्या: YCS-MP-BHO-0001"
try:
    draw.text((10, 10), hindi_text, fill='black', font=font_bold)
    test_img.save('test_hindi_font.png')
    print("✓ Hindi text rendered successfully - saved as test_hindi_font.png")
except Exception as e:
    print(f"✗ Failed to render Hindi text: {e}")

print("\nFont test complete!")