#!/usr/bin/env python
"""
Manual Data Integrity Checker
Quick verification of vibhag and campaign data saving
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration, VibhagOption

def check_specific_registration(reg_id):
    """Check specific registration data integrity"""
    try:
        reg = EventRegistration.objects.get(id=reg_id)
        print(f"📋 Registration {reg_id} - {reg.full_name}")
        print(f"   Type: {reg.registration_type}")
        
        # Check vibhags
        print(f"\n🏢 Vibhag Data:")
        print(f"   Raw: {reg.selected_vibhags}")
        
        if reg.selected_vibhags:
            try:
                vibhag_ids = [int(vid) for vid in reg.selected_vibhags if str(vid).isdigit()]
                vibhags = VibhagOption.objects.filter(id__in=vibhag_ids)
                names = [v.name for v in vibhags]
                print(f"   Names: {names}")
                print(f"   Export: {reg.get_vibhag_names()}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Check campaigns
        print(f"\n📢 Campaign Data:")
        print(f"   Raw: {reg.selected_campaigns}")
        
        if reg.selected_campaigns:
            try:
                campaign_dict = dict(EventRegistration.CAMPAIGN_CHOICES)
                names = [campaign_dict.get(code, code) for code in reg.selected_campaigns]
                print(f"   Names: {names}")
                print(f"   Export: {reg.get_campaign_names()}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return True
        
    except EventRegistration.DoesNotExist:
        print(f"❌ Registration {reg_id} not found")
        return False
    except Exception as e:
        print(f"❌ Error checking registration {reg_id}: {e}")
        return False

def check_recent_volunteers():
    """Check recent volunteer registrations"""
    print("🔍 Checking recent volunteer registrations...\n")
    
    volunteers = EventRegistration.objects.filter(
        registration_type='volunteer'
    ).order_by('-id')[:5]
    
    if not volunteers:
        print("❌ No volunteer registrations found")
        return
    
    for vol in volunteers:
        check_specific_registration(vol.id)
        print("-" * 50)

def main():
    print("🚀 Manual Data Integrity Check\n")
    
    # Check recent volunteers
    check_recent_volunteers()
    
    # Check specific registration if provided
    import sys
    if len(sys.argv) > 1:
        try:
            reg_id = int(sys.argv[1])
            print(f"\n🎯 Checking specific registration {reg_id}:")
            check_specific_registration(reg_id)
        except ValueError:
            print("❌ Invalid registration ID provided")

if __name__ == "__main__":
    main()