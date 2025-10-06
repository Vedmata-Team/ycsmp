from django.contrib import admin
from django import forms
from django.db import models
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Event, EventRegistration, EventImage, ApprovalUser, ResponsibilityOption, VibhagOption, UpZone, Country, State, City
from .admin_filters import UpZoneFilter
from .models_location import StateDistrict
from .models_warning import SiteWarning

from .admin_upzone import UpZoneAdmin
from .export_utils import ExportManager, EVENT_FIELDS, REGISTRATION_FIELDS, APPROVAL_USER_FIELDS

class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1

class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0
    readonly_fields = ('registration_number', 'registration_date')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'event_date', 'registered_count', 'available_spots', 'is_published')
    list_filter = ('category', 'is_published', 'is_featured', 'event_date')
    search_fields = ('title', 'description', 'venue')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [EventImageInline, EventRegistrationInline]
    list_editable = ('is_published',)
    date_hierarchy = 'event_date'
    actions = ['export_csv', 'export_excel', 'export_pdf']
    
    fieldsets = (
        ('मुख्य जानकारी', {
            'fields': ('title', 'slug', 'description', 'venue')
        }),
        ('वर्गीकरण', {
            'fields': ('category',)
        }),
        ('तिथि और समय', {
            'fields': ('event_date', 'registration_deadline')
        }),
        ('पंजीकरण सेटिंग्स', {
            'fields': ('registration_fee', 'max_participants')
        }),
        ('प्रकाशन सेटिंग्स', {
            'fields': ('is_published', 'is_featured')
        })
    )
    
    def export_csv(self, request, queryset):
        return ExportManager.export_to_csv(queryset, 'events_export', EVENT_FIELDS)
    export_csv.short_description = "Export to CSV"
    
    def export_excel(self, request, queryset):
        return ExportManager.export_to_excel(queryset, 'events_export', EVENT_FIELDS)
    export_excel.short_description = "Export to Excel"
    
    def export_pdf(self, request, queryset):
        return ExportManager.export_to_pdf(queryset, 'events_export', EVENT_FIELDS, 'Events Report')
    export_pdf.short_description = "Export to PDF"

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    class Media:
        js = ('admin/js/bulk_approval_progress.js', 'admin/js/final_approval_with_idcard.js')
    list_display = ('registration_number_with_buttons', 'full_name', 'registration_type', 'email', 'phone', 'village_taluka', 'city', 'state', 'country', 'arrival_date', 'approval_status_with_user', 'email_sent', 'registration_date_ist', 'is_confirmed')
    list_filter = ('approval_status', 'event', 'registration_type', 'state', 'city', UpZoneFilter, 'responsibility', 'gender', 'email_sent', 'is_confirmed', 'registration_date', 'transport_mode', 'previous_shivir', 'arrival_date')
    actions = ['approve_district', 'approve_upzone', 'approve_final', 'reject_registration', 'send_email_to_approved', 'export_csv', 'export_excel', 'export_pdf']
    search_fields = ('full_name', 'email', 'phone', 'registration_number', 'education', 'occupation')
    readonly_fields = ('registration_number', 'registration_date', 'approval_history_display')
    list_editable = ('is_confirmed',)
    date_hierarchy = 'registration_date'
    show_full_result_count = False
    list_per_page = 25
    list_max_show_all = 25
    preserve_filters = True
    
    fieldsets = (
        ('पंजीकरण जानकारी', {
            'fields': ('registration_number', 'event', 'registration_type', 'registration_date')
        }),
        ('व्यक्तिगत जानकारी', {
            'fields': ('full_name', 'phone', 'email', 'date_of_birth', 'gender', 'responsibility', 'education', 'occupation', 'special_skills')
        }),
        ('पता जानकारी', {
            'fields': ('village_taluka', 'city', 'state', 'country')
        }),
        ('परिवहन जानकारी', {
            'fields': ('transport_mode', 'vehicle_number')
        }),
('दस्तावेज़ अपलोड', {
            'fields': ('aadhar_upload_type', 'get_aadhar_full_display', 'get_aadhar_front_display', 'get_aadhar_back_display', 'get_passport_photo_display')
        }),
        ('अन्य जानकारी', {
            'fields': ('previous_shivir', 'gayatri_diksha', 'arrival_date', 'interested_in_volunteering', 'volunteering_details', 'get_campaign_names', 'get_vibhag_names')
        }),
        ('अप्रूवल स्थिति', {
            'fields': ('approval_status', 'approval_history_display', 'district_approver', 'district_approved_at_ist', 'upzone_approver', 'upzone_approved_at_ist', 'final_approver', 'final_approved_at_ist', 'rejected_by', 'rejected_at', 'rejection_reason', 'email_sent')
        }),
        ('स्थिति', {
            'fields': ('is_confirmed', 'payment_status')
        })
    )
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        is_edit_mode = request.GET.get('edit') == '1'
        
        if not request.user.is_superuser:
            # Remove स्थिति fieldset for staff users
            fieldsets = [fs for fs in fieldsets if fs[0] != 'स्थिति']
        
        # Hide document upload section for non-participant registrations
        if obj and obj.registration_type != 'participant':
            fieldsets = [fs for fs in fieldsets if fs[0] != 'दस्तावेज़ अपलोड']
        
        # Add mode indicator to first fieldset
        if fieldsets and obj:
            mode_text = "Edit Mode" if is_edit_mode else "View & Approve Mode"
            first_fieldset = list(fieldsets[0])
            if len(first_fieldset) > 1 and isinstance(first_fieldset[1], dict):
                first_fieldset[1] = dict(first_fieldset[1])
                first_fieldset[1]['description'] = f"<strong style='color: {'#dc3545' if is_edit_mode else '#28a745'};'>{mode_text}</strong>"
                fieldsets[0] = tuple(first_fieldset)
        
        return fieldsets
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        readonly.extend(['get_vibhag_names', 'get_campaign_names', 'get_aadhar_full_display', 'get_aadhar_front_display', 'get_aadhar_back_display', 'get_passport_photo_display', 'approval_history_display', 'district_approved_at_ist', 'upzone_approved_at_ist', 'final_approved_at_ist', 'registration_date_ist'])
        if obj:
            readonly.extend(['district_approved_at', 'upzone_approved_at', 'final_approved_at', 'email_sent'])
        
        # Check if this is edit mode
        is_edit_mode = request.GET.get('edit') == '1'
        
        # Non-superusers cannot edit final approval fields
        if not request.user.is_superuser:
            readonly.extend(['final_approver', 'final_approved_at', 'registration_number', 'district_approver', 'upzone_approver', 'rejected_by', 'rejected_at', 'email_sent'])
            # Only make approval_status readonly if user has no approval permissions or registration is fully approved
            try:
                approval_user = ApprovalUser.objects.get(user=request.user)
                # Don't make approval_status readonly for approval users unless already fully approved
                if obj and obj.approval_status == 'approved' and not is_edit_mode:
                    readonly.extend(['approval_status'])
            except ApprovalUser.DoesNotExist:
                # Non-approval users can't change approval status
                readonly.extend(['approval_status'])
        else:
            # Even superusers can't edit approver fields if already set (unless in edit mode)
            if obj and not is_edit_mode:
                if obj.district_approver:
                    readonly.append('district_approver')
                if obj.upzone_approver:
                    readonly.append('upzone_approver')
                if obj.final_approver:
                    readonly.append('final_approver')
        
        # Make email_sent readonly always (it's auto-managed)
        readonly.append('email_sent')
        
        # In view mode (not edit mode), make most fields readonly
        if not is_edit_mode and obj:
            readonly.extend([
                'full_name', 'phone', 'email', 'date_of_birth', 'gender', 'responsibility',
                'education', 'occupation', 'village_taluka', 'city', 'state', 'country',
                'transport_mode', 'vehicle_number', 'previous_shivir', 'arrival_date',
                'interested_in_volunteering', 'volunteering_details', 'special_skills',
                'volunteer_start_date', 'volunteer_end_date'
            ])
        
        return readonly
    
    def get_approval_buttons(self, request, obj):
        """Get available approval buttons based on user permissions"""
        if not obj:
            return []
        
        buttons = []
        
        try:
            approval_user = ApprovalUser.objects.get(user=request.user)
            
            # Check if user can approve this registration type
            if approval_user.allowed_registration_types and obj.registration_type not in approval_user.allowed_registration_types:
                return buttons
            
            # Super Approver can approve at ALL levels
            if approval_user.is_super_approver:
                if obj.approval_status == 'pending':
                    buttons.append({
                        'name': '_approve_district',
                        'label': 'जिला अप्रूव करें',
                        'class': 'btn-success'
                    })
                elif obj.approval_status == 'district_approved':
                    buttons.append({
                        'name': '_approve_upzone',
                        'label': 'उपजोन अप्रूव करें',
                        'class': 'btn-primary'
                    })
                elif obj.approval_status == 'upzone_approved':
                    buttons.append({
                        'name': '_approve_final',
                        'label': 'अंतिम अप्रूव करें',
                        'class': 'btn-warning'
                    })
                
                # Reject button for super approvers
                if obj.approval_status != 'approved' and obj.approval_status != 'rejected':
                    buttons.append({
                        'name': '_reject',
                        'label': 'अस्वीकृत करें',
                        'class': 'btn-danger'
                    })
                return buttons
            
            # District level approval
            if (approval_user.is_district_approver and 
                obj.approval_status == 'pending' and 
                obj.matches_approval_user(approval_user)):
                buttons.append({
                    'name': '_approve_district',
                    'label': 'जिला अप्रूव करें',
                    'class': 'btn-success'
                })
            
            # UpZone level approval
            if (approval_user.is_upzone_approver and 
                obj.approval_status == 'district_approved' and 
                obj.matches_approval_user(approval_user)):
                buttons.append({
                    'name': '_approve_upzone',
                    'label': 'उपजोन अप्रूव करें',
                    'class': 'btn-primary'
                })
            
            # State level approval
            if (approval_user.is_state_approver and 
                obj.approval_status == 'upzone_approved'):
                buttons.append({
                    'name': '_approve_final',
                    'label': 'अंतिम अप्रूव करें',
                    'class': 'btn-warning'
                })
            
            # Reject button (available at any level if not already approved)
            if obj.approval_status != 'approved' and obj.approval_status != 'rejected':
                buttons.append({
                    'name': '_reject',
                    'label': 'अस्वीकृत करें',
                    'class': 'btn-danger'
                })
        
        except ApprovalUser.DoesNotExist:
            # Superuser can always approve
            if request.user.is_superuser:
                if obj.approval_status == 'pending':
                    buttons.append({'name': '_approve_district', 'label': 'जिला अप्रूव करें', 'class': 'btn-success'})
                elif obj.approval_status == 'district_approved':
                    buttons.append({'name': '_approve_upzone', 'label': 'उपजोन अप्रूव करें', 'class': 'btn-primary'})
                elif obj.approval_status == 'upzone_approved':
                    buttons.append({'name': '_approve_final', 'label': 'अंतिम अप्रूव करें', 'class': 'btn-warning'})
                
                if obj.approval_status != 'approved':
                    buttons.append({'name': '_reject', 'label': 'अस्वीकृत करें', 'class': 'btn-danger'})
        
        return buttons
    
    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request, obj, **kwargs)
        
        class DynamicEventRegistrationForm(form_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                
                # Set default approver to logged-in user
                if 'district_approver' in self.fields:
                    if not obj or not obj.district_approver:
                        self.fields['district_approver'].initial = request.user
                    if not request.user.is_superuser:
                        self.fields['district_approver'].widget.attrs['readonly'] = True
                        self.fields['district_approver'].widget.attrs['style'] = 'pointer-events: none; background-color: #f8f9fa;'
                
                if 'upzone_approver' in self.fields:
                    if not obj or not obj.upzone_approver:
                        self.fields['upzone_approver'].initial = request.user
                    if not request.user.is_superuser:
                        self.fields['upzone_approver'].widget.attrs['readonly'] = True
                        self.fields['upzone_approver'].widget.attrs['style'] = 'pointer-events: none; background-color: #f8f9fa;'
                
                if 'final_approver' in self.fields:
                    if not obj or not obj.final_approver:
                        self.fields['final_approver'].initial = request.user
                    # Only superusers can change approver
                    if not request.user.is_superuser:
                        self.fields['final_approver'].widget.attrs['readonly'] = True
                        self.fields['final_approver'].widget.attrs['style'] = 'pointer-events: none; background-color: #f8f9fa;'
                
                # Auto-set rejected_by for non-superusers
                if 'rejected_by' in self.fields:
                    if not request.user.is_superuser:
                        self.fields['rejected_by'].initial = request.user
                        self.fields['rejected_by'].widget.attrs['readonly'] = True
                        self.fields['rejected_by'].widget.attrs['style'] = 'pointer-events: none; background-color: #f8f9fa;'
                
                # Restrict approval status choices based on user type
                if 'approval_status' in self.fields:
                    try:
                        approval_user = ApprovalUser.objects.get(user=request.user)
                        if approval_user.is_super_approver:
                            # Super approvers can set any status
                            self.fields['approval_status'].choices = [
                                ('pending', 'प्रतीक्षारत'),
                                ('district_approved', 'जिला अप्रूव'),
                                ('upzone_approved', 'उपजोन अप्रूव'),
                                ('approved', 'अप्रूव'),
                                ('rejected', 'अस्वीकृत')
                            ]
                        elif approval_user.is_district_approver:
                            self.fields['approval_status'].choices = [
                                ('pending', 'प्रतीक्षारत'),
                                ('district_approved', 'जिला अप्रूव'),
                                ('rejected', 'अस्वीकृत')
                            ]
                        elif approval_user.is_upzone_approver:
                            self.fields['approval_status'].choices = [
                                ('district_approved', 'जिला अप्रूव'),
                                ('upzone_approved', 'उपजोन अप्रूव'),
                                ('rejected', 'अस्वीकृत')
                            ]
                        elif approval_user.is_state_approver:
                            self.fields['approval_status'].choices = [
                                ('upzone_approved', 'उपजोन अप्रूव'),
                                ('approved', 'अप्रूव'),
                                ('rejected', 'अस्वीकृत')
                            ]
                    except ApprovalUser.DoesNotExist:
                        pass
        
        return DynamicEventRegistrationForm
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        
        # Keep export actions for superusers only
        if not request.user.is_superuser:
            for action in ['export_csv', 'export_excel', 'export_pdf']:
                if action in actions:
                    del actions[action]
        
        try:
            approval_user = ApprovalUser.objects.get(user=request.user)
            # Super approvers get ALL actions
            if approval_user.is_super_approver:
                # Keep all actions for super approvers
                pass
            # Keep actions based on user level - allow what they can do
            elif approval_user.is_district_approver:
                # District approvers can do district approval and rejection
                if 'approve_upzone' in actions:
                    del actions['approve_upzone']
                if 'approve_final' in actions:
                    del actions['approve_final']
            elif approval_user.is_upzone_approver:
                # UpZone approvers can do upzone approval and rejection
                if 'approve_district' in actions:
                    del actions['approve_district']
                if 'approve_final' in actions:
                    del actions['approve_final']
            elif approval_user.is_state_approver:
                # State approvers can do final approval and rejection
                if 'approve_district' in actions:
                    del actions['approve_district']
                if 'approve_upzone' in actions:
                    del actions['approve_upzone']
            # Keep reject_registration, send_email_to_approved, and send_email_to_rejected for all approval users
        except ApprovalUser.DoesNotExist:
            # Non-approval users (except superusers) get no bulk actions
            if not request.user.is_superuser:
                for action in ['approve_district', 'approve_upzone', 'approve_final', 'reject_registration', 'send_email_to_approved', 'send_email_to_rejected']:
                    if action in actions:
                        del actions[action]
        return actions
    
    def approve_district(self, request, queryset):
        from django.utils import timezone
        from django.db import transaction
        updated = 0
        skipped = 0
        batch_size = 20
        
        # Check user permissions
        try:
            approval_user = ApprovalUser.objects.get(user=request.user)
            if not (approval_user.is_district_approver or approval_user.is_super_approver or request.user.is_superuser):
                self.message_user(request, 'आपको जिला अप्रूवल का अधिकार नहीं है।', level='error')
                return
        except ApprovalUser.DoesNotExist:
            if not request.user.is_superuser:
                self.message_user(request, 'आपको अप्रूवल का अधिकार नहीं है।', level='error')
                return
        
        registrations = list(queryset)
        
        # Process in batches
        for i in range(0, len(registrations), batch_size):
            batch = registrations[i:i+batch_size]
            
            with transaction.atomic():
                for registration in batch:
                    if registration.approval_status == 'pending':
                        # Check if user can approve this registration
                        try:
                            if not request.user.is_superuser and not approval_user.is_super_approver and not registration.matches_approval_user(approval_user):
                                skipped += 1
                                continue
                        except:
                            pass
                        
                        registration.approval_status = 'district_approved'
                        registration.district_approver = request.user
                        registration.district_approved_at = timezone.now()
                        registration.save()
                        updated += 1
                    else:
                        skipped += 1
        
        message = f'{updated} पंजीकरण जिला अप्रूव किए गए।'
        if skipped > 0:
            message += f' {skipped} छोड़े गए (गलत स्थिति या अधिकार नहीं)।'
        self.message_user(request, message)
    approve_district.short_description = "जिला अप्रूव करें"
    
    def approve_upzone(self, request, queryset):
        from django.utils import timezone
        from django.db import transaction
        updated = 0
        skipped = 0
        batch_size = 20
        
        # Check user permissions
        try:
            approval_user = ApprovalUser.objects.get(user=request.user)
            if not (approval_user.is_upzone_approver or approval_user.is_super_approver or request.user.is_superuser):
                self.message_user(request, 'आपको उपजोन अप्रूवल का अधिकार नहीं है।', level='error')
                return
        except ApprovalUser.DoesNotExist:
            if not request.user.is_superuser:
                self.message_user(request, 'आपको अप्रूवल का अधिकार नहीं है।', level='error')
                return
        
        registrations = list(queryset)
        
        # Process in batches
        for i in range(0, len(registrations), batch_size):
            batch = registrations[i:i+batch_size]
            
            with transaction.atomic():
                for registration in batch:
                    if registration.approval_status == 'district_approved':
                        # Check if user can approve this registration
                        try:
                            if not request.user.is_superuser and not approval_user.is_super_approver and not registration.matches_approval_user(approval_user):
                                skipped += 1
                                continue
                        except:
                            pass
                        
                        registration.approval_status = 'upzone_approved'
                        registration.upzone_approver = request.user
                        registration.upzone_approved_at = timezone.now()
                        registration.save()
                        updated += 1
                    else:
                        skipped += 1
        
        message = f'{updated} पंजीकरण उपजोन अप्रूव किए गए।'
        if skipped > 0:
            message += f' {skipped} छोड़े गए (गलत स्थिति या अधिकार नहीं)।'
        self.message_user(request, message)
    approve_upzone.short_description = "उपजोन अप्रूव करें"
    
    def approve_final(self, request, queryset):
        from django.utils import timezone
        from django.db import transaction
        from .email_utils import send_registration_approval_email
        from django.http import StreamingHttpResponse
        import json
        import time
        
        # Check if AJAX request for streaming
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self._stream_bulk_approval(request, queryset)
        
        updated = 0
        email_sent = 0
        batch_size = 25
        
        # Check user permissions
        can_final_approve = request.user.is_superuser
        if not can_final_approve:
            try:
                approval_user = ApprovalUser.objects.get(user=request.user)
                can_final_approve = approval_user.is_state_approver or approval_user.is_super_approver
            except ApprovalUser.DoesNotExist:
                pass
        
        if not can_final_approve:
            self.message_user(request, 'आपको अंतिम अप्रूवल का अधिकार नहीं है।', level='error')
            return
        
        registrations = list(queryset.exclude(approval_status='approved'))
        total = len(registrations)
        
        if total > 100:
            self.message_user(request, f'एक साथ 100 से अधिक ({total}) प्रोसेस नहीं कर सकते। छोटे बैच में करें।', level='error')
            return
        
        try:
            # Process in batches with combined email sending
            for i in range(0, len(registrations), batch_size):
                batch = registrations[i:i+batch_size]
                
                with transaction.atomic():
                    now = timezone.now()
                    
                    for registration in batch:
                        # Update approval status
                        registration.approval_status = 'approved'
                        registration.final_approver = request.user
                        registration.final_approved_at = now
                        registration.is_confirmed = True
                        
                        # Generate registration number if needed
                        if not registration.registration_number:
                            registration.registration_number = registration.generate_registration_number()
                        
                        # Skip auto email to prevent duplicate
                        registration._skip_auto_email = True
                        registration.save()
                        updated += 1
                        
                        # Send combined email with attachments
                        try:
                            if send_registration_approval_email(registration, request.user):
                                registration.email_sent = True
                                registration.save(update_fields=['email_sent'])
                                email_sent += 1
                        except Exception as e:
                            print(f"Email failed for {registration.email}: {e}")
                        
                        # Small delay between emails
                        time.sleep(0.3)
            
            message = f'{updated} पंजीकरण अप्रूव किए गए, {email_sent} ईमेल भेजे गए।'
            self.message_user(request, message)
                
        except Exception as e:
            self.message_user(request, f'प्रोसेसिंग में त्रुटि: {str(e)}', level='error')
    
    def _stream_bulk_approval(self, request, queryset):
        from django.utils import timezone
        from django.db import transaction
        from .email_utils import send_registration_approval_email
        from django.http import StreamingHttpResponse
        import json
        import time
        
        def generate_progress():
            registrations = list(queryset.exclude(approval_status='approved'))
            total = len(registrations)
            updated = 0
            email_sent = 0
            
            yield f"data: {json.dumps({'progress': 0, 'message': 'प्रारंभ हो रहा है...', 'step': 'starting'})}\n\n"
            
            for i, registration in enumerate(registrations):
                try:
                    with transaction.atomic():
                        now = timezone.now()
                        
                        # Update approval status
                        registration.approval_status = 'approved'
                        registration.final_approver = request.user
                        registration.final_approved_at = now
                        registration.is_confirmed = True
                        
                        # Generate registration number if needed
                        if not registration.registration_number:
                            registration.registration_number = registration.generate_registration_number()
                        
                        # Skip auto email to prevent duplicate
                        registration._skip_auto_email = True
                        registration.save()
                        updated += 1
                        
                        # Send combined email with attachments
                        try:
                            if send_registration_approval_email(registration, request.user):
                                registration.email_sent = True
                                registration.save(update_fields=['email_sent'])
                                email_sent += 1
                        except Exception as e:
                            print(f"Email failed for {registration.email}: {e}")
                        
                        # Calculate progress
                        progress = int(((i + 1) / total) * 100)
                        message = f'{i + 1}/{total} पंजीकरण प्रोसेस हुए'
                        
                        yield f"data: {json.dumps({'progress': progress, 'message': message, 'step': 'processing'})}\n\n"
                        
                        # Small delay
                        time.sleep(0.3)
                        
                except Exception as e:
                    yield f"data: {json.dumps({'progress': 0, 'message': f'त्रुटि: {str(e)}', 'step': 'error'})}\n\n"
            
            # Final completion message
            final_message = f'{updated} पंजीकरण अप्रूव, {email_sent} ईमेल भेजे गए'
            yield f"data: {json.dumps({'progress': 100, 'message': final_message, 'step': 'completed'})}\n\n"
        
        response = StreamingHttpResponse(generate_progress(), content_type='text/plain')
        response['Cache-Control'] = 'no-cache'
        return response
    approve_final.short_description = "अंतिम अप्रूव करें"
    
    def reject_registration(self, request, queryset):
        from django.utils import timezone
        updated = 0
        skipped = 0
        
        # Check user permissions
        try:
            approval_user = ApprovalUser.objects.get(user=request.user)
        except ApprovalUser.DoesNotExist:
            if not request.user.is_superuser:
                self.message_user(request, 'आपको अस्वीकृत करने का अधिकार नहीं है।', level='error')
                return
            approval_user = None
        
        for registration in queryset:
            if registration.approval_status not in ['approved', 'rejected']:
                # Check if user can reject this registration
                can_reject = request.user.is_superuser
                if not can_reject and approval_user:
                    can_reject = approval_user.is_super_approver or registration.matches_approval_user(approval_user)
                
                if can_reject:
                    registration.approval_status = 'rejected'
                    if hasattr(registration, 'rejected_by'):
                        registration.rejected_by = request.user
                        registration.rejected_at = timezone.now()
                    registration.save()
                    updated += 1
                else:
                    skipped += 1
            else:
                skipped += 1
        
        message = f'{updated} पंजीकरण अस्वीकृत किए गए।'
        if skipped > 0:
            message += f' {skipped} छोड़े गए (पहले से अप्रूव/अस्वीकृत या अधिकार नहीं)।'
        self.message_user(request, message)
    reject_registration.short_description = "पंजीकरण अस्वीकृत करें"
    
    def send_email_to_approved(self, request, queryset):
        from .email_utils import send_registration_approval_email
        import time
        
        approved_regs = list(queryset.filter(approval_status='approved'))
        total = len(approved_regs)
        
        # Limit bulk emails to prevent spam
        if total > 100:
            self.message_user(request, f'एक साथ 100 से अधिक ({total}) ईमेल नहीं भेज सकते। छोटे बैच में करें।', level='error')
            return
        
        sent_count = 0
        failed_count = 0
        
        for i, registration in enumerate(approved_regs):
            try:
                if send_registration_approval_email(registration, request.user):
                    registration.email_sent = True
                    registration.save(update_fields=['email_sent'])
                    sent_count += 1
                else:
                    failed_count += 1
                
                # Add delay every 10 emails to prevent spam
                if (i + 1) % 10 == 0:
                    time.sleep(2)
                    
            except Exception as e:
                failed_count += 1
                time.sleep(1)  # Extra delay on error
        
        if failed_count > 0:
            self.message_user(request, f'{sent_count} ईमेल भेजे गए, {failed_count} असफल।')
        else:
            self.message_user(request, f'{sent_count} पंजीकरण विवरण ईमेल भेजे गए।')
    send_email_to_approved.short_description = "अप्रूव पंजीकरण को ईमेल भेजें"
    

    
    def registration_number_with_buttons(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        
        buttons = []
        reg_num = obj.registration_number or '-'
        
        # View & Approve button
        view_url = reverse('admin:events_eventregistration_change', args=[obj.pk])
        buttons.append(f'<a href="{view_url}" class="button" style="padding: 3px 8px; background: #28a745; color: white; text-decoration: none; border-radius: 3px; font-size: 11px; margin-right: 5px;">View & Approve</a>')
        
        # Edit button
        edit_url = f"{reverse('admin:events_eventregistration_change', args=[obj.pk])}?edit=1"
        buttons.append(f'<a href="{edit_url}" class="button" style="padding: 3px 8px; background: #007cba; color: white; text-decoration: none; border-radius: 3px; font-size: 11px; margin-right: 5px;">Edit</a>')
        
        # Email button for approved registrations
        if obj.approval_status == 'approved' and obj.registration_number:
            email_url = reverse('events:resend_email', args=[obj.pk])
            buttons.append(f'<a href="{email_url}" class="button" style="padding: 3px 8px; background: #ffc107; color: black; text-decoration: none; border-radius: 3px; font-size: 11px; margin-right: 5px;">Send Email</a>')
        
        # Vehicle pass button for approved registrations with valid vehicle info
        if (obj.approval_status == 'approved' and 
            obj.vehicle_number and 
            obj.vehicle_number.strip() and 
            obj.vehicle_number != '-' and 
            obj.transport_mode == 'car'):
            from django.urls import reverse
            from urllib.parse import quote
            vehicle_pass_url = reverse('vehicle_pass:generate', args=[obj.pk, quote(obj.vehicle_number, safe='')])
            buttons.append(f'<a href="{vehicle_pass_url}" class="button" style="padding: 3px 8px; background: #17a2b8; color: white; text-decoration: none; border-radius: 3px; font-size: 11px;">Vehicle Pass</a>')
        
        return format_html(f'{reg_num}<br>{"".join(buttons)}')
    
    registration_number_with_buttons.short_description = 'पंजीकरण संख्या / Actions'
    registration_number_with_buttons.allow_tags = True
    
    def get_vibhag_names(self, obj):
        if obj.selected_vibhags:
            try:
                vibhag_ids = [int(vid) for vid in obj.selected_vibhags if str(vid).isdigit()]
                vibhags = VibhagOption.objects.filter(id__in=vibhag_ids)
                return ', '.join([v.name for v in vibhags])
            except:
                return str(obj.selected_vibhags)
        return '-'
    get_vibhag_names.short_description = 'चयनित विभाग'
    
    def get_campaign_names(self, obj):
        if obj.selected_campaigns:
            campaign_dict = dict(EventRegistration.CAMPAIGN_CHOICES)
            campaign_names = [campaign_dict.get(code, code) for code in obj.selected_campaigns]
            return ', '.join(campaign_names)
        return '-'
    get_campaign_names.short_description = 'चयनित अभियान'
    
    def get_aadhar_full_display(self, obj):
        from django.utils.html import format_html
        if obj.aadhar_full and str(obj.aadhar_full).strip():
            url = str(obj.aadhar_full)
            return format_html(
                '<div style="border: 2px solid green; padding: 5px; border-radius: 5px;">'
                '<a href="{}" target="_blank"><img src="{}" style="max-width: 100px; max-height: 60px;"/></a>'
                '<br><small style="color: green;">✓ Uploaded</small>'
                '</div>', url, url
            )
        else:
            return format_html(
                '<div style="border: 2px solid red; padding: 5px; border-radius: 5px; text-align: center;">'
                '<span style="color: red;">✗ Not Uploaded</span>'
                '</div>'
            )
    get_aadhar_full_display.short_description = 'पूरा आधार कार्ड'
    
    def get_aadhar_front_display(self, obj):
        from django.utils.html import format_html
        if obj.aadhar_front:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="max-width: 100px; max-height: 60px;"/></a>', obj.aadhar_front, obj.aadhar_front)
        return '-'
    get_aadhar_front_display.short_description = 'आधार कार्ड (आगे)'
    
    def get_aadhar_back_display(self, obj):
        from django.utils.html import format_html
        if obj.aadhar_back:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="max-width: 100px; max-height: 60px;"/></a>', obj.aadhar_back, obj.aadhar_back)
        return '-'
    get_aadhar_back_display.short_description = 'आधार कार्ड (पीछे)'
    
    def get_passport_photo_display(self, obj):
        from django.utils.html import format_html
        if obj.passport_photo and str(obj.passport_photo).strip():
            url = str(obj.passport_photo)
            return format_html(
                '<div style="border: 2px solid green; padding: 5px; border-radius: 5px;">'
                '<a href="{}" target="_blank"><img src="{}" style="max-width: 100px; max-height: 60px;"/></a>'
                '<br><small style="color: green;">✓ Uploaded</small>'
                '</div>', url, url
            )
        else:
            return format_html(
                '<div style="border: 2px solid red; padding: 5px; border-radius: 5px; text-align: center;">'
                '<span style="color: red;">✗ Not Uploaded</span>'
                '</div>'
            )
    get_passport_photo_display.short_description = 'पासपोर्ट फोटो'
    
    def approval_status_with_user(self, obj):
        return obj.get_approval_status_display_with_user()
    approval_status_with_user.short_description = 'अप्रूवल स्थिति (अप्रूवर के साथ)'
    
    def approval_history_display(self, obj):
        return obj.get_approval_history()
    approval_history_display.short_description = 'अप्रूवल इतिहास'
    
    def district_approved_at_ist(self, obj):
        if obj.district_approved_at:
            from django.utils import timezone
            local_time = timezone.localtime(obj.district_approved_at)
            return local_time.strftime('%d/%m/%Y %H:%M:%S IST')
        return '-'
    district_approved_at_ist.short_description = 'जिला अप्रूवल समय (IST)'
    
    def upzone_approved_at_ist(self, obj):
        if obj.upzone_approved_at:
            from django.utils import timezone
            local_time = timezone.localtime(obj.upzone_approved_at)
            return local_time.strftime('%d/%m/%Y %H:%M:%S IST')
        return '-'
    upzone_approved_at_ist.short_description = 'उपजोन अप्रूवल समय (IST)'
    
    def final_approved_at_ist(self, obj):
        if obj.final_approved_at:
            from django.utils import timezone
            local_time = timezone.localtime(obj.final_approved_at)
            return local_time.strftime('%d/%m/%Y %H:%M:%S IST')
        return '-'
    final_approved_at_ist.short_description = 'अंतिम अप्रूवल समय (IST)'
    
    def registration_date_ist(self, obj):
        if obj.registration_date:
            from django.utils import timezone
            local_time = timezone.localtime(obj.registration_date)
            return local_time.strftime('%d/%m/%Y %H:%M:%S IST')
        return '-'
    registration_date_ist.short_description = 'पंजीकरण तिथि (IST)'
    

    
    def get_responsibility_name(self, obj):
        if obj.registration_type == 'organization_representative' and obj.responsibility:
            return obj.responsibility.name
        return '-'
    get_responsibility_name.short_description = 'जिम्मेदारी/पदनाम'
    
    def get_queryset(self, request):
        """Optimized queryset with select_related for better performance"""
        qs = super().get_queryset(request)
        
        # Use select_related for foreign keys to reduce database queries
        qs = qs.select_related(
            'event',
            'responsibility', 
            'district_approver',
            'upzone_approver',
            'final_approver'
        )
        
        # Superusers can see all registrations
        if request.user.is_superuser:
            return qs
        
        # Staff users with 'view all registrations' permission can see everything
        if request.user.has_perm('events.view_all_eventregistration'):
            return qs
        
        # Check if user has approval permissions
        try:
            approval_user = ApprovalUser.objects.get(user=request.user)
            
            # Super approvers can see all registrations
            if approval_user.is_super_approver:
                return qs
            

            
            # For MP state - filter by assigned districts/upzones
            if approval_user.state_code == 'MP':
                if approval_user.is_district_approver and approval_user.districts:
                    # District level - filter by assigned districts
                    filtered_qs = qs.filter(
                        city__in=approval_user.districts,
                        approval_status__in=['pending', 'district_approved', 'upzone_approved', 'approved']
                    ).filter(
                        models.Q(state__icontains='madhya pradesh') |
                        models.Q(state__iexact='MP')
                    )
                    # Filter by allowed registration types if specified
                    if approval_user.allowed_registration_types:
                        filtered_qs = filtered_qs.filter(registration_type__in=approval_user.allowed_registration_types)

                    return filtered_qs
                    
                elif approval_user.is_upzone_approver and approval_user.upzone:
                    # UpZone level - filter by upzone districts
                    upzone_districts = approval_user.upzone.districts or []

                    
                    if upzone_districts:
                        # Show all registrations from upzone districts (pending to approved)
                        filtered_qs = qs.filter(
                            city__in=upzone_districts
                        ).filter(
                            models.Q(state__icontains='madhya pradesh') |
                            models.Q(state__iexact='MP')
                        )

                        
                        return filtered_qs
                    else:

                        return qs.none()
                        
                elif approval_user.is_state_approver:
                    # State level - all MP registrations
                    filtered_qs = qs.filter(
                        models.Q(state__icontains='madhya pradesh') |
                        models.Q(state__iexact='MP')
                    )

                    return filtered_qs
                else:

                    return qs.none()
            
            # For other states - filter by state
            elif approval_user.is_state_approver:
                state_name = self.get_state_name_from_code(approval_user.state_code)
                if state_name:
                    filtered_qs = qs.filter(
                        models.Q(state__iexact=state_name) |
                        models.Q(state__iexact=approval_user.state_code)
                    )
                else:
                    filtered_qs = qs.filter(state__iexact=approval_user.state_code)

                return filtered_qs
            
            else:

                return qs.none()
                
        except ApprovalUser.DoesNotExist:

            return qs.none()
        except Exception as e:

            return qs.none()
    
    def get_state_name_from_code(self, state_code):
        """Get state name from state code using CSV"""
        try:
            from django.conf import settings
            import csv
            import os
            csv_path = os.path.join(settings.STATICFILES_DIRS[0], 'csv', 'states.csv')
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['state_code'] == state_code:
                        return row['name']
        except:
            pass
        return None
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Add approval buttons to change view context"""
        extra_context = extra_context or {}
        
        if object_id:
            obj = self.get_object(request, object_id)
            if obj:
                extra_context['approval_buttons'] = self.get_approval_buttons(request, obj)
        
        return super().change_view(request, object_id, form_url, extra_context)
    
    def response_change(self, request, obj):
        from django.http import HttpResponseRedirect
        from django.utils import timezone
        from django.contrib import messages
        
        # Handle custom approval buttons
        if '_approve_district' in request.POST:
            if obj.approval_status == 'pending':
                obj.approval_status = 'district_approved'
                obj.district_approver = request.user
                obj.district_approved_at = timezone.now()
                obj.save()
                messages.success(request, f'Registration {obj.registration_number or obj.full_name} has been district approved.')
            return HttpResponseRedirect(request.path)
        
        elif '_approve_upzone' in request.POST:
            if obj.approval_status == 'district_approved':
                obj.approval_status = 'upzone_approved'
                obj.upzone_approver = request.user
                obj.upzone_approved_at = timezone.now()
                obj.save()
                messages.success(request, f'Registration {obj.registration_number or obj.full_name} has been upzone approved.')
            return HttpResponseRedirect(request.path)
        
        elif '_approve_final' in request.POST:
            if obj.approval_status == 'upzone_approved':
                obj.approval_status = 'approved'
                obj.final_approver = request.user
                obj.final_approved_at = timezone.now()
                obj._skip_auto_email = True  # Skip auto email
                obj.save()  # This will generate registration number but skip email
                messages.success(request, f'Registration {obj.registration_number} has been finally approved. Use Send Email button for combined email with attachments.')
            return HttpResponseRedirect(request.path)
        
        elif '_reject' in request.POST:
            if obj.approval_status != 'approved':
                obj.approval_status = 'rejected'
                obj.save()
                messages.warning(request, f'Registration {obj.registration_number or obj.full_name} has been rejected.')
            return HttpResponseRedirect(request.path)
        
        return super().response_change(request, obj)
    
    def save_model(self, request, obj, form, change):
        from django.utils import timezone
        from django.contrib import messages
        
        # Check if is_confirmed status changed to True
        send_confirmation_email = False
        if change and obj.pk:
            old_obj = EventRegistration.objects.get(pk=obj.pk)
            if not old_obj.is_confirmed and obj.is_confirmed and not old_obj.email_sent:
                send_confirmation_email = True
        elif not change and obj.is_confirmed:
            send_confirmation_email = True
        
        # Auto-assign approvers when status changes
        if obj.approval_status == 'district_approved' and not obj.district_approver:
            obj.district_approver = request.user
            if not obj.district_approved_at:
                obj.district_approved_at = timezone.now()
        
        if obj.approval_status == 'upzone_approved' and not obj.upzone_approver:
            obj.upzone_approver = request.user
            if not obj.upzone_approved_at:
                obj.upzone_approved_at = timezone.now()
        
        # Auto-assign final_approver when status changes to approved
        if obj.approval_status == 'approved' and not obj.final_approver:
            obj.final_approver = request.user
            if not obj.final_approved_at:
                obj.final_approved_at = timezone.now()
        
        # Check if JavaScript requested to skip auto email or if email already sent
        if request.POST.get('_skip_auto_email') or obj.email_sent:
            obj._skip_auto_email = True
        
        # Auto-assign rejected_by when status changes to rejected
        if obj.approval_status == 'rejected' and not getattr(obj, 'rejected_by', None):
            obj.rejected_by = request.user
            if not getattr(obj, 'rejected_at', None):
                obj.rejected_at = timezone.now()
        
        # For non-superusers, ensure they can only set themselves as approver
        if not request.user.is_superuser:
            if obj.approval_status == 'district_approved':
                obj.district_approver = request.user
            elif obj.approval_status == 'upzone_approved':
                obj.upzone_approver = request.user
            elif obj.approval_status == 'approved':
                obj.final_approver = request.user
            elif obj.approval_status == 'rejected':
                obj.rejected_by = request.user
        
        super().save_model(request, obj, form, change)
        
        # AUTO EMAIL DISABLED - Use Send Email button for combined email with attachments
        if send_confirmation_email and not obj.email_sent:
            messages.info(request, f'🚫 Auto email disabled for {obj.email} - use Send Email button for combined email with attachments')
        elif obj.email_sent:
            messages.info(request, f'Email already sent to {obj.email}')
    
    def export_csv(self, request, queryset):
        return ExportManager.export_to_csv(queryset, 'registrations_export', REGISTRATION_FIELDS)
    export_csv.short_description = "Export to CSV"
    
    def export_excel(self, request, queryset):
        return ExportManager.export_to_excel(queryset, 'registrations_export', REGISTRATION_FIELDS)
    export_excel.short_description = "Export to Excel"
    
    def export_pdf(self, request, queryset):
        return ExportManager.export_to_pdf(queryset, 'registrations_export', REGISTRATION_FIELDS, 'Registrations Report')
    export_pdf.short_description = "Export to PDF"
    
    def changelist_view(self, request, extra_context=None):
        if '_facets' not in request.GET:
            from django.http import HttpResponseRedirect
            from django.urls import reverse
            url = reverse('admin:events_eventregistration_changelist')
            return HttpResponseRedirect(f'{url}?_facets=True')
        return super().changelist_view(request, extra_context)

@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ('event', 'caption', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('event__title', 'caption')

# Removed EventRegistrationAdminForm as it's now handled dynamically

# Register UpZone admin from separate file

@admin.register(SiteWarning)
class SiteWarningAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'message')
    list_editable = ('is_active',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('चेतावनी जानकारी', {
            'fields': ('title', 'message', 'is_active')
        }),
    )

class ApprovalUserForm(forms.ModelForm):
    districts = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'searchable-districts'}),
        required=False,
        label="जिले (केवल जिला अप्रूवर के लिए)"
    )
    
    allowed_registration_types = forms.MultipleChoiceField(
        choices=EventRegistration.REGISTRATION_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="अनुमतित पंजीकरण प्रकार"
    )
    
    class Meta:
        model = ApprovalUser
        fields = '__all__'
        widgets = {
            'state_code': forms.Select(choices=[])
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['state_code'].widget.choices = self.get_state_choices()
        self.fields['districts'].choices = self.get_mp_district_choices()
    
    def get_state_choices(self):
        choices = []
        try:
            from django.conf import settings
            import csv
            import os
            csv_path = os.path.join(settings.STATICFILES_DIRS[0], 'csv', 'states.csv')
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get('country_code') == 'IN':
                        choices.append((row['state_code'], f"{row['name']} ({row['state_code']})"))
        except:
            pass
        return choices
    
    def get_mp_district_choices(self):
        choices = []
        try:
            from django.conf import settings
            import csv
            import os
            csv_path = os.path.join(settings.STATICFILES_DIRS[0], 'csv', 'cities.csv')
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get('state_code') == 'MP':
                        choices.append((row['name'], row['name']))
        except:
            pass
        return sorted(list(set(choices)))
        
        if self.instance.pk:
            if self.instance.districts:
                self.fields['districts'].initial = self.instance.districts
            if self.instance.allowed_registration_types:
                self.fields['allowed_registration_types'].initial = self.instance.allowed_registration_types
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.districts = list(self.cleaned_data.get('districts', []))
        instance.allowed_registration_types = list(self.cleaned_data.get('allowed_registration_types', []))
        if commit:
            instance.save()
        return instance

@admin.register(ApprovalUser)
class ApprovalUserAdmin(admin.ModelAdmin):
    form = ApprovalUserForm
    list_display = ('user', 'state_code', 'is_super_approver', 'is_state_approver', 'is_district_approver', 'is_upzone_approver', 'get_assignment_display')
    list_filter = ('state_code', 'is_super_approver', 'is_state_approver', 'is_district_approver', 'is_upzone_approver', 'upzone')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    actions = ['export_csv', 'export_excel', 'export_pdf']
    
    fieldsets = (
        ('यूजर जानकारी', {
            'fields': ('user', 'state_code')
        }),
        ('अधिकार स्तर (केवल एक चुनें)', {
            'fields': ('is_super_approver', 'is_state_approver', 'is_upzone_approver', 'is_district_approver'),
            'description': 'केवल एक अधिकार स्तर चुनें - सुपर, राज्य, उपजोन, या जिला'
        }),
        ('असाइनमेंट', {
            'fields': ('upzone', 'districts', 'allowed_registration_types'),
            'description': 'उपजोन अप्रूवर के लिए उपजोन चुनें, जिला अप्रूवर के लिए जिले चुनें, और अनुमतित पंजीकरण प्रकार चुनें'
        })
    )
    
    def get_assignment_display(self, obj):
        return obj.get_assignment_display()
    get_assignment_display.short_description = 'असाइनमेंट'
    
    class Media:
        js = ('admin/js/approval_user.js', 'admin/js/approval_user_upzone.js')
        css = {
            'all': ('admin/css/approval_user.css',)
        }
    
    def export_csv(self, request, queryset):
        return ExportManager.export_to_csv(queryset, 'approval_users_export', APPROVAL_USER_FIELDS)
    export_csv.short_description = "Export to CSV"
    
    def export_excel(self, request, queryset):
        return ExportManager.export_to_excel(queryset, 'approval_users_export', APPROVAL_USER_FIELDS)
    export_excel.short_description = "Export to Excel"
    
    def export_pdf(self, request, queryset):
        return ExportManager.export_to_pdf(queryset, 'approval_users_export', APPROVAL_USER_FIELDS, 'Approval Users Report')
    export_pdf.short_description = "Export to PDF"

@admin.register(ResponsibilityOption)
class ResponsibilityOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    list_editable = ('order', 'is_active')
    ordering = ('order', 'name')
    
    fieldsets = (
        ('जिम्मेदारी जानकारी', {
            'fields': ('name', 'order', 'is_active')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('order', 'name')

@admin.register(VibhagOption)
class VibhagOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    list_editable = ('order', 'is_active')
    ordering = ('order', 'name')
    
    fieldsets = (
        ('विभाग जानकारी', {
            'fields': ('name', 'order', 'is_active')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('order', 'name')

# StateDistrict admin access removed

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'country')
    list_filter = ('country',)
    search_fields = ('name', 'code')
    ordering = ('country', 'name')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')
    list_filter = ('state__country', 'state')
    search_fields = ('name', 'state__name')
    ordering = ('state', 'name')


