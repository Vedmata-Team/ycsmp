from PIL import Image
import os

# Analyze ID card images
static_path = "static/ID_Card"
images = ["Participants_ID Card_.png", "Volunteers_ID Card_.png", "Organization_ID Card_.png"]

for img_name in images:
    img_path = os.path.join(static_path, img_name)
    if os.path.exists(img_path):
        with Image.open(img_path) as img:
            width, height = img.size
            dpi = img.info.get('dpi', (72, 72))
            
            # Convert pixels to cm at 300 DPI
            width_cm = (width / 300) * 2.54
            height_cm = (height / 300) * 2.54
            
            print(f"{img_name}:")
            print(f"  Pixels: {width} x {height}")
            print(f"  DPI: {dpi}")
            print(f"  Size (cm): {width_cm:.2f} x {height_cm:.2f}")
            print(f"  Mode: {img.mode}")
            print()
    else:
        print(f"{img_name}: File not found")