#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import ResponsibilityOption

def create_default_responsibilities():
    """Create default responsibility options"""
    responsibilities = [
        ('जिला युवा समन्वयक', 1),
        ('उपजोन समन्वयक', 2),
        ('क्षेत्रीय समन्वयक', 3),
        ('प्रांतीय समन्वयक', 4),
        ('राष्ट्रीय समन्वयक', 5),
        ('शाखा प्रमुख', 6),
        ('केंद्र प्रमुख', 7),
        ('संगठन सचिव', 8),
        ('कार्यकारी सदस्य', 9),
        ('सलाहकार', 10),
    ]
    
    created_count = 0
    for responsibility, order in responsibilities:
        obj, created = ResponsibilityOption.objects.get_or_create(
            name=responsibility,
            defaults={'is_active': True, 'order': order}
        )
        if created:
            created_count += 1
            print(f"Created: {responsibility} (Order: {order})")
        else:
            print(f"Already exists: {responsibility}")
            if obj.order == 0:
                obj.order = order
                obj.save()
                print(f"  Updated order to: {order}")
    
    print(f"\nTotal created: {created_count}")
    print(f"Total responsibilities: {ResponsibilityOption.objects.count()}")

if __name__ == '__main__':
    create_default_responsibilities()