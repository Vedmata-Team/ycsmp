from PIL import Image
import os

# Folder containing JPG images
image_folder = r"C:\Users\divym\OneDrive\Documents\GitHub\ycsmp\ID_Cards_Export\Organizations"

# Output PDF path
output_pdf = r"C:\Users\divym\OneDrive\Desktop\Organisations_ID_Cards.pdf"

# Get all JPG files, sorted by filename
images = [f for f in os.listdir(image_folder) if f.lower().endswith(".jpg")]
images.sort()  # ensures sequence based on filename

# Open images and convert to RGB
img_list = []
for img_file in images:
    img_path = os.path.join(image_folder, img_file)
    im = Image.open(img_path)
    if im.mode != "RGB":
        im = im.convert("RGB")
    img_list.append(im)

# Save all images into a single PDF
if img_list:
    first_image = img_list.pop(0)
    first_image.save(output_pdf, save_all=True, append_images=img_list)

print(f"✅ PDF created successfully at {output_pdf}")
