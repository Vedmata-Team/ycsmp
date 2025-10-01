import os
import requests
from pathlib import Path

# Create fonts directory
fonts_dir = Path("static/fonts")
fonts_dir.mkdir(exist_ok=True)

# Download Poppins fonts from Google Fonts
fonts_to_download = {
    "Poppins-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf",
    "Poppins-Medium.ttf": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Medium.ttf", 
    "Poppins-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf"
}

for font_name, url in fonts_to_download.items():
    font_path = fonts_dir / font_name
    if not font_path.exists():
        print(f"Downloading {font_name}...")
        response = requests.get(url)
        if response.status_code == 200:
            with open(font_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ Downloaded {font_name}")
        else:
            print(f"✗ Failed to download {font_name}")
    else:
        print(f"✓ {font_name} already exists")

print("Font download complete!")