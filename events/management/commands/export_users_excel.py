from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import EventRegistration
import pandas as pd
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Export all registered users to Excel with separate sheets for approved and non-approved users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='exports',
            help='Output directory for the Excel file (default: exports)'
        )
        parser.add_argument(
            '--filename',
            type=str,
            help='Custom filename for the Excel file'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting user data export...'))
        
        # Create output directory if it doesn't exist
        output_dir = options['output_dir']
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.stdout.write(f'Created directory: {output_dir}')

        # Generate filename
        if options['filename']:
            filename = options['filename']
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'user_registrations_{timestamp}.xlsx'
        
        filepath = os.path.join(output_dir, filename)

        try:
            # Get all registrations
            all_registrations = EventRegistration.objects.select_related(
                'event', 'responsibility', 'district_approver', 'upzone_approver', 
                'final_approver', 'rejected_by'
            ).all()

            self.stdout.write(f'Found {all_registrations.count()} total registrations')

            # Separate approved and non-approved users
            approved_users = all_registrations.filter(approval_status='approved')
            non_approved_users = all_registrations.exclude(approval_status='approved')

            self.stdout.write(f'Approved users: {approved_users.count()}')
            self.stdout.write(f'Non-approved users: {non_approved_users.count()}')

            # Prepare data for Excel
            def prepare_registration_data(registrations):
                data = []
                for reg in registrations:
                    row = {
                        'Registration Number': reg.registration_number or 'Not Generated',
                        'Full Name': reg.full_name,
                        'Phone': reg.phone,
                        'Email': reg.email,
                        'Date of Birth': reg.date_of_birth.strftime('%d/%m/%Y') if reg.date_of_birth else '',
                        'Gender': reg.get_gender_display(),
                        'Registration Type': reg.get_registration_type_display(),
                        'Event': reg.event.title,
                        'State': reg.state,
                        'District/City': reg.city,
                        'Village/Taluka': reg.village_taluka,
                        'Country': reg.country,
                        'Education': reg.get_education_display(),
                        'Occupation': reg.occupation or '',
                        'Transport Mode': reg.get_transport_mode_display(),
                        'Vehicle Number': reg.vehicle_number or '',
                        'Arrival Date': reg.get_arrival_date_display(),
                        'Previous Shivir': 'Yes' if reg.previous_shivir else 'No',
                        'Gayatri Diksha': 'Yes' if reg.gayatri_diksha else ('No' if reg.gayatri_diksha is False else 'Not Specified'),
                        'Special Skills': reg.special_skills_other or '',
                        'Selected Campaigns': reg.get_campaign_names(),
                        'Selected Vibhags': reg.get_vibhag_names(),
                        'Responsibility': reg.responsibility.name if reg.responsibility else '',
                        'Volunteer Start Date': reg.volunteer_start_date.strftime('%d/%m/%Y') if reg.volunteer_start_date else '',
                        'Volunteer End Date': reg.volunteer_end_date.strftime('%d/%m/%Y') if reg.volunteer_end_date else '',
                        'Interested in Volunteering': 'Yes' if reg.interested_in_volunteering else 'No',
                        'Volunteering Details': reg.volunteering_details or '',
                        'Approval Status': reg.get_approval_status_display(),
                        'District Approver': reg.district_approver.get_full_name() if reg.district_approver else '',
                        'District Approved At': reg.district_approved_at.strftime('%d/%m/%Y %H:%M') if reg.district_approved_at else '',
                        'UpZone Approver': reg.upzone_approver.get_full_name() if reg.upzone_approver else '',
                        'UpZone Approved At': reg.upzone_approved_at.strftime('%d/%m/%Y %H:%M') if reg.upzone_approved_at else '',
                        'Final Approver': reg.final_approver.get_full_name() if reg.final_approver else '',
                        'Final Approved At': reg.final_approved_at.strftime('%d/%m/%Y %H:%M') if reg.final_approved_at else '',
                        'Rejected By': reg.rejected_by.get_full_name() if reg.rejected_by else '',
                        'Rejected At': reg.rejected_at.strftime('%d/%m/%Y %H:%M') if reg.rejected_at else '',
                        'Rejection Reason': reg.rejection_reason or '',
                        'Registration Date': reg.registration_date.strftime('%d/%m/%Y %H:%M'),
                        'Payment Status': 'Paid' if reg.payment_status else 'Pending',
                        'Email Sent': 'Yes' if reg.email_sent else 'No',
                        'Is Confirmed': 'Yes' if reg.is_confirmed else 'No',
                        'Aadhar Upload Type': reg.aadhar_upload_type or '',
                        'Aadhar Full URL': reg.aadhar_full or '',
                        'Aadhar Front URL': reg.aadhar_front or '',
                        'Aadhar Back URL': reg.aadhar_back or '',
                        'Passport Photo URL': reg.passport_photo or '',
                    }
                    data.append(row)
                return data

            # Create Excel writer
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Approved users sheet
                if approved_users.exists():
                    approved_data = prepare_registration_data(approved_users)
                    approved_df = pd.DataFrame(approved_data)
                    approved_df.to_excel(writer, sheet_name='Approved Users', index=False)
                    self.stdout.write(f'✓ Approved users sheet created with {len(approved_data)} records')

                # Non-approved users sheet
                if non_approved_users.exists():
                    non_approved_data = prepare_registration_data(non_approved_users)
                    non_approved_df = pd.DataFrame(non_approved_data)
                    non_approved_df.to_excel(writer, sheet_name='Non-Approved Users', index=False)
                    self.stdout.write(f'✓ Non-approved users sheet created with {len(non_approved_data)} records')

                # Summary sheet
                summary_data = [
                    ['Total Registrations', all_registrations.count()],
                    ['Approved Users', approved_users.count()],
                    ['Pending Users', all_registrations.filter(approval_status='pending').count()],
                    ['District Approved Users', all_registrations.filter(approval_status='district_approved').count()],
                    ['UpZone Approved Users', all_registrations.filter(approval_status='upzone_approved').count()],
                    ['Rejected Users', all_registrations.filter(approval_status='rejected').count()],
                    ['Participants', all_registrations.filter(registration_type='participant').count()],
                    ['Volunteers', all_registrations.filter(registration_type='volunteer').count()],
                    ['Organization Representatives', all_registrations.filter(registration_type='organization_representative').count()],
                    ['Export Date', timezone.now().strftime('%d/%m/%Y %H:%M:%S')],
                ]
                
                summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Count'])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                self.stdout.write('✓ Summary sheet created')

            self.stdout.write(
                self.style.SUCCESS(f'✅ Export completed successfully!')
            )
            self.stdout.write(f'📁 File saved: {filepath}')
            self.stdout.write(f'📊 Total records exported: {all_registrations.count()}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Export failed: {str(e)}')
            )
            raise e