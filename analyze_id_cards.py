#!/usr/bin/env python3
"""
Analyze ID Card dimensions and properties
"""

import os
from PIL import Image

def analyze_id_cards():
    """Analyze all ID card images with dimensions in cm"""
    print("🔍 Analyzing ID Card Images")
    print("=" * 50)
    
    id_card_path = "static/ID_Card"
    
    if not os.path.exists(id_card_path):
        print("❌ ID_Card folder not found")
        return
    
    cards = []
    
    for filename in os.listdir(id_card_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(id_card_path, filename)
            
            try:
                with Image.open(filepath) as img:
                    width_px, height_px = img.size
                    file_size = os.path.getsize(filepath)
                    
                    # Get DPI (default to 300 if not available)
                    dpi = img.info.get('dpi', (300, 300))
                    if isinstance(dpi, tuple):
                        dpi_x, dpi_y = dpi
                    else:
                        dpi_x = dpi_y = dpi
                    
                    # Convert pixels to cm (1 inch = 2.54 cm)
                    width_cm = round((width_px / dpi_x) * 2.54, 2)
                    height_cm = round((height_px / dpi_y) * 2.54, 2)
                    
                    card_info = {
                        'filename': filename,
                        'width_px': width_px,
                        'height_px': height_px,
                        'width_cm': width_cm,
                        'height_cm': height_cm,
                        'dpi': dpi_x,
                        'aspect_ratio': round(width_px/height_px, 2),
                        'file_size_kb': round(file_size/1024, 1),
                        'format': img.format,
                        'mode': img.mode
                    }
                    
                    cards.append(card_info)
                    
            except Exception as e:
                print(f"❌ Error analyzing {filename}: {e}")
    
    # Display results
    for card in cards:
        print(f"\n📄 {card['filename']}")
        print(f"   Dimensions: {card['width_cm']} x {card['height_cm']} cm")
        print(f"   Pixels: {card['width_px']} x {card['height_px']} px")
        print(f"   DPI: {card['dpi']}")
        print(f"   Aspect Ratio: {card['aspect_ratio']}:1")
        print(f"   File Size: {card['file_size_kb']} KB")
        print(f"   Format: {card['format']} ({card['mode']})")
        
        # Determine card type
        if 'participant' in card['filename'].lower():
            card_type = "Participant ID Card"
        elif 'volunteer' in card['filename'].lower():
            card_type = "Volunteer ID Card"
        elif 'organization' in card['filename'].lower():
            card_type = "Organization ID Card"
        else:
            card_type = "Unknown Type"
        
        print(f"   Type: {card_type}")
    
    # Summary
    if cards:
        print(f"\n📊 Summary:")
        print(f"   Total Cards: {len(cards)}")
        
        widths_cm = [c['width_cm'] for c in cards]
        heights_cm = [c['height_cm'] for c in cards]
        
        print(f"   Width Range: {min(widths_cm)} - {max(widths_cm)} cm")
        print(f"   Height Range: {min(heights_cm)} - {max(heights_cm)} cm")
        
        # Check if all cards have same dimensions
        if len(set(widths_cm)) == 1 and len(set(heights_cm)) == 1:
            print(f"   ✅ All cards have consistent dimensions: {widths_cm[0]} x {heights_cm[0]} cm")
        else:
            print(f"   ⚠️  Cards have different dimensions")
        
        # Standard ID card size comparison (8.56 x 5.398 cm)
        standard_width_cm = 8.56
        standard_height_cm = 5.398
        
        print(f"\n🎯 Standard ID Card Comparison:")
        print(f"   Standard Size: {standard_width_cm} x {standard_height_cm} cm")
        
        for card in cards:
            width_diff = round(card['width_cm'] - standard_width_cm, 2)
            height_diff = round(card['height_cm'] - standard_height_cm, 2)
            
            print(f"   {card['filename']}:")
            print(f"     Width: {'+' if width_diff >= 0 else ''}{width_diff} cm from standard")
            print(f"     Height: {'+' if height_diff >= 0 else ''}{height_diff} cm from standard")

if __name__ == "__main__":
    analyze_id_cards()