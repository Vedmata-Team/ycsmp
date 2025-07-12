from django.contrib import admin
from django import forms
from django.db import models
from .models import Event, EventRegistration, EventImage, ApprovalUser
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
    list_display = ('registration_number_with_email_button', 'full_name', 'event', 'email', 'phone', 'approval_status', 'email_sent', 'registration_date', 'is_confirmed')
    list_filter = ('event', 'city', 'gender', 'approval_status', 'email_sent', 'is_confirmed', 'registration_date', 'transport_mode', 'previous_shivir')
    actions = ['approve_level1', 'approve_final', 'reject_registration', 'send_email_to_approved', 'export_csv', 'export_excel', 'export_pdf']
    search_fields = ('full_name', 'email', 'phone', 'registration_number', 'education', 'occupation')
    readonly_fields = ('registration_number', 'registration_date')
    list_editable = ('is_confirmed',)
    
    fieldsets = (
        ('पंजीकरण जानकारी', {
            'fields': ('registration_number', 'event', 'registration_date')
        }),
        ('व्यक्तिगत जानकारी', {
            'fields': ('full_name', 'phone', 'email', 'date_of_birth', 'gender', 'education', 'occupation', 'special_skills')
        }),
        ('पता जानकारी', {
            'fields': ('village_taluka', 'city', 'state', 'country')
        }),
        ('परिवहन जानकारी', {
            'fields': ('transport_mode', 'vehicle_number')
        }),
        ('अन्य जानकारी', {
            'fields': ('previous_shivir', 'arrival_date', 'departure_date', 'interested_in_volunteering', 'volunteering_details', 'selected_campaigns')
        }),
        ('अप्रूवल स्थिति', {
            'fields': ('approval_status', 'level1_approver', 'level1_approved_at', 'final_approver', 'final_approved_at', 'rejection_reason', 'email_sent')
        }),
        ('स्थिति', {
            'fields': ('is_confirmed', 'payment_status')
        })
    )
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        if not request.user.is_superuser:
            # Remove स्थिति fieldset for staff users
            fieldsets = [fs for fs in fieldsets if fs[0] != 'स्थिति']
        return fieldsets
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:
            readonly.extend(['selected_campaigns', 'level1_approved_at', 'final_approved_at', 'email_sent'])
        
        # Level 1 approvers cannot edit final approval fields
        if not request.user.is_superuser:
            readonly.extend(['final_approver', 'final_approved_at', 'registration_number', 'level1_approver', 'email_sent'])
            if obj and obj.approval_status in ['approved', 'level1_approved']:
                readonly.extend(['approval_status'])
        
        return readonly
    
    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request, obj, **kwargs)
        
        class DynamicEventRegistrationForm(form_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                # Restrict approval status choices for non-superusers
                if not request.user.is_superuser and 'approval_status' in self.fields:
                    self.fields['approval_status'].choices = [
                        ('pending', 'प्रतीक्षारत'),
                        ('level1_approved', 'स्तर 1 अप्रूव'),
                        ('rejected', 'अस्वीकृत')
                    ]
        
        return DynamicEventRegistrationForm
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        # Remove final approval action for non-superusers
        if not request.user.is_superuser and 'approve_final' in actions:
            del actions['approve_final']
        return actions
    
    def approve_level1(self, request, queryset):
        from django.utils import timezone
        updated = 0
        for registration in queryset.filter(approval_status='pending'):
            registration.approval_status = 'level1_approved'
            registration.level1_approver = request.user
            registration.level1_approved_at = timezone.now()
            registration.save()
            updated += 1
        self.message_user(request, f'{updated} पंजीकरण स्तर 1 अप्रूव किए गए।')
    approve_level1.short_description = "स्तर 1 अप्रूव करें"
    
    def approve_final(self, request, queryset):
        from django.utils import timezone
        updated = 0
        for registration in queryset.filter(approval_status='level1_approved'):
            registration.approval_status = 'approved'
            registration.final_approver = request.user
            registration.final_approved_at = timezone.now()
            registration.save()  # This will generate registration number
            updated += 1
        self.message_user(request, f'{updated} पंजीकरण अंतिम अप्रूव किए गए।')
    approve_final.short_description = "अंतिम अप्रूव करें"
    
    def reject_registration(self, request, queryset):
        updated = queryset.update(approval_status='rejected')
        self.message_user(request, f'{updated} पंजीकरण अस्वीकृत किए गए।')
    reject_registration.short_description = "पंजीकरण अस्वीकृत करें"
    
    def send_email_to_approved(self, request, queryset):
        from .email_utils import send_registration_details_email
        sent_count = 0
        for registration in queryset.filter(approval_status='approved'):
            if send_registration_details_email(registration):
                registration.email_sent = True
                registration.save(update_fields=['email_sent'])
                sent_count += 1
        self.message_user(request, f'{sent_count} पंजीकरण विवरण ईमेल भेजे गए।')
    send_email_to_approved.short_description = "अप्रूव पंजीकरण को ईमेल भेजें"
    
    def registration_number_with_email_button(self, obj):
        if obj.approval_status == 'approved' and obj.registration_number:
            from django.urls import reverse
            from django.utils.html import format_html
            url = reverse('events:resend_email', args=[obj.pk])
            return format_html(
                '{} <a href="{}" class="button" style="margin-left: 10px; padding: 5px 10px; background: #007cba; color: white; text-decoration: none; border-radius: 3px; font-size: 12px;">ईमेल भेजें</a>',
                obj.registration_number, url
            )
        return obj.registration_number or '-'
    registration_number_with_email_button.short_description = 'पंजीकरण संख्या'
    registration_number_with_email_button.allow_tags = True
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Superusers can see all registrations
        if request.user.is_superuser:
            return qs
        
        # Check if user has approval permissions
        try:
            approval_user = ApprovalUser.objects.get(user=request.user)
            
            # For MP state - filter by assigned districts
            if approval_user.state_code == 'MP' and approval_user.is_district_approver:
                if approval_user.districts:
                    # Filter by city (district) and also check state to be safe
                    return qs.filter(
                        city__in=approval_user.districts,
                        state__icontains='madhya pradesh'
                    ) | qs.filter(
                        city__in=approval_user.districts,
                        state__iexact='MP'
                    )
                else:
                    return qs.none()  # No districts assigned
            
            # For other states - filter by state
            elif approval_user.is_state_approver:
                # Get state name from state code and filter by multiple variations
                state_name = self.get_state_name_from_code(approval_user.state_code)
                if state_name:
                    return qs.filter(
                        models.Q(state__iexact=state_name) |
                        models.Q(state__iexact=approval_user.state_code)
                    )
                else:
                    # Fallback to state code only
                    return qs.filter(state__iexact=approval_user.state_code)
            
            else:
                return qs.none()  # User has no approval permissions
                
        except ApprovalUser.DoesNotExist:
            # User is not an approval user, show no registrations
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
    
    def save_model(self, request, obj, form, change):
        # Auto-assign level1_approver for non-superusers
        if not request.user.is_superuser and obj.approval_status == 'level1_approved' and not obj.level1_approver:
            obj.level1_approver = request.user
            if not obj.level1_approved_at:
                from django.utils import timezone
                obj.level1_approved_at = timezone.now()
        super().save_model(request, obj, form, change)
    
    def export_csv(self, request, queryset):
        return ExportManager.export_to_csv(queryset, 'registrations_export', REGISTRATION_FIELDS)
    export_csv.short_description = "Export to CSV"
    
    def export_excel(self, request, queryset):
        return ExportManager.export_to_excel(queryset, 'registrations_export', REGISTRATION_FIELDS)
    export_excel.short_description = "Export to Excel"
    
    def export_pdf(self, request, queryset):
        return ExportManager.export_to_pdf(queryset, 'registrations_export', REGISTRATION_FIELDS, 'Registrations Report')
    export_pdf.short_description = "Export to PDF"

@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ('event', 'caption', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('event__title', 'caption')

# Removed EventRegistrationAdminForm as it's now handled dynamically

class ApprovalUserForm(forms.ModelForm):
    districts = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'searchable-districts'}),
        required=False,
        label="जिले (केवल MP के लिए)"
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
        
        if self.instance.pk and self.instance.districts:
            self.fields['districts'].initial = self.instance.districts
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.districts = list(self.cleaned_data.get('districts', []))
        if commit:
            instance.save()
        return instance

@admin.register(ApprovalUser)
class ApprovalUserAdmin(admin.ModelAdmin):
    form = ApprovalUserForm
    list_display = ('user', 'state_code', 'is_state_approver', 'is_district_approver', 'get_assignment_display')
    list_filter = ('state_code', 'is_state_approver', 'is_district_approver')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    actions = ['export_csv', 'export_excel', 'export_pdf']
    
    fieldsets = (
        ('यूजर जानकारी', {
            'fields': ('user', 'state_code')
        }),
        ('अधिकार', {
            'fields': ('is_state_approver', 'is_district_approver', 'districts')
        }),
        ('असाइनमेंट जानकारी', {
            'fields': (),
            'description': 'इस यूजर को असाइन किए गए जिले/राज्य की जानकारी देखने के लिए सेव करें।'
        })
    )
    
    def get_assignment_display(self, obj):
        return obj.get_assignment_display()
    get_assignment_display.short_description = 'असाइनमेंट'
    
    class Media:
        js = ('admin/js/approval_user.js',)
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
