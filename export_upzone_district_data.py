#!/usr/bin/env python3
"""
Export upzone and district-wise registration data with counts by type and approval status
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration, UpZone

def export_upzone_district_data():
    """Export upzone and district wise registration data"""
    
    print("📊 Exporting UpZone and District Registration Data")
    print("=" * 60)
    
    # Create exports folder
    exports_dir = "exports"
    os.makedirs(exports_dir, exist_ok=True)
    
    # Get all upzones
    upzones = UpZone.objects.all()
    
    if not upzones.exists():
        print("❌ No upzones found")
        return False
    
    all_data = []
    
    for upzone in upzones:
        print(f"\n🔄 Processing UpZone: {upzone.name}")
        
        # Get districts for this upzone
        districts = upzone.districts or []
        
        if not districts:
            print(f"  ⚠️ No districts assigned to {upzone.name}")
            continue
        
        for district in districts:
            print(f"  📍 Processing District: {district}")
            
            # Get all registrations for this district
            district_regs = EventRegistration.objects.filter(
                city=district,
                state__in=['Madhya Pradesh', 'MP']
            )
            
            # Count by registration type
            participant_count = district_regs.filter(registration_type='participant').count()
            volunteer_count = district_regs.filter(registration_type='volunteer').count()
            org_count = district_regs.filter(registration_type='organization_representative').count()
            
            # Count by approval status
            pending_count = district_regs.filter(approval_status='pending').count()
            district_approved_count = district_regs.filter(approval_status='district_approved').count()
            upzone_approved_count = district_regs.filter(approval_status='upzone_approved').count()
            approved_count = district_regs.filter(approval_status='approved').count()
            rejected_count = district_regs.filter(approval_status='rejected').count()
            
            total_count = district_regs.count()
            
            # Add to data
            row_data = {
                'UpZone': upzone.name,
                'District': district,
                'Total_Registrations': total_count,
                'Participants': participant_count,
                'Volunteers': volunteer_count,
                'Organizations': org_count,
                'Pending': pending_count,
                'District_Approved': district_approved_count,
                'UpZone_Approved': upzone_approved_count,
                'Final_Approved': approved_count,
                'Rejected': rejected_count
            }
            
            all_data.append(row_data)
            
            print(f"    Total: {total_count} | P:{participant_count} V:{volunteer_count} O:{org_count} | Approved:{approved_count}")
    
    if not all_data:
        print("❌ No data to export")
        return False
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Sort by UpZone and District
    df = df.sort_values(['UpZone', 'District'])
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"upzone_district_registrations_{timestamp}.xlsx"
    filepath = os.path.join(exports_dir, filename)
    
    # Export to Excel with formatting
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Main data sheet
        df.to_excel(writer, sheet_name='UpZone_District_Data', index=False)
        
        # Summary sheet
        summary_data = []
        
        # UpZone summary
        for upzone in upzones:
            upzone_data = df[df['UpZone'] == upzone.name]
            if not upzone_data.empty:
                summary_row = {
                    'UpZone': upzone.name,
                    'Districts_Count': len(upzone_data),
                    'Total_Registrations': upzone_data['Total_Registrations'].sum(),
                    'Participants': upzone_data['Participants'].sum(),
                    'Volunteers': upzone_data['Volunteers'].sum(),
                    'Organizations': upzone_data['Organizations'].sum(),
                    'Final_Approved': upzone_data['Final_Approved'].sum(),
                    'Approval_Rate': f"{(upzone_data['Final_Approved'].sum() / upzone_data['Total_Registrations'].sum() * 100):.1f}%" if upzone_data['Total_Registrations'].sum() > 0 else "0%"
                }
                summary_data.append(summary_row)
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='UpZone_Summary', index=False)
        
        # Overall totals
        totals_data = [{
            'Metric': 'Total UpZones',
            'Value': len(upzones)
        }, {
            'Metric': 'Total Districts',
            'Value': df['District'].nunique()
        }, {
            'Metric': 'Total Registrations',
            'Value': df['Total_Registrations'].sum()
        }, {
            'Metric': 'Total Participants',
            'Value': df['Participants'].sum()
        }, {
            'Metric': 'Total Volunteers',
            'Value': df['Volunteers'].sum()
        }, {
            'Metric': 'Total Organizations',
            'Value': df['Organizations'].sum()
        }, {
            'Metric': 'Total Approved',
            'Value': df['Final_Approved'].sum()
        }, {
            'Metric': 'Overall Approval Rate',
            'Value': f"{(df['Final_Approved'].sum() / df['Total_Registrations'].sum() * 100):.1f}%" if df['Total_Registrations'].sum() > 0 else "0%"
        }]
        
        totals_df = pd.DataFrame(totals_data)
        totals_df.to_excel(writer, sheet_name='Overall_Totals', index=False)
    
    print(f"\n✅ Export completed successfully!")
    print(f"📁 File saved: {filepath}")
    print(f"📊 Data exported:")
    print(f"   - {len(upzones)} UpZones")
    print(f"   - {df['District'].nunique()} Districts")
    print(f"   - {df['Total_Registrations'].sum()} Total Registrations")
    print(f"   - {df['Final_Approved'].sum()} Approved Registrations")
    
    return True

if __name__ == "__main__":
    try:
        success = export_upzone_district_data()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Export failed: {str(e)}")
        sys.exit(1)