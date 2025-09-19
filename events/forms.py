from django import forms
from .models import EventRegistration, ResponsibilityOption, VibhagOption
import csv
import os
from django.conf import settings


class BaseEventRegistrationForm(forms.ModelForm):
    # Campaign choices as checkboxes
    campaigns = forms.MultipleChoiceField(
        choices=EventRegistration.CAMPAIGN_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="अभियान चयन करें"
    )
    
    # Special skills as checkboxes
    special_skills = forms.MultipleChoiceField(
        choices=EventRegistration.SPECIAL_SKILLS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="विशेष कौशल"
    )
    
    # Other special skills text field
    special_skills_other = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'अन्य विशेष कौशल लिखें'}),
        label="अन्य विशेष कौशल"
    )
    
    # Override arrival_date to accept dynamic values
    arrival_date = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label="आगमन तिथि"
    )
    
    # Vibhag selection for volunteers
    vibhags = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="कार्य विभाग चुनें"
    )
    
    # Gayatri Diksha field
    gayatri_diksha = forms.ChoiceField(
        choices=[(True, 'हाँ'), (False, 'नहीं')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=False,
        label="क्या आपने गायत्री दीक्षा ली है?"
    )
    
    def get_state_choices(self):
        choices = [('', 'राज्य चुनें')]
        try:
            csv_path = os.path.join(settings.STATICFILES_DIRS[0], 'csv', 'states.csv')
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get('country_code') == 'IN':
                        choices.append((row['name'], row['name']))
        except:
            pass
        return choices
    
    class Meta:
        model = EventRegistration
        fields = [
            'full_name', 'phone', 'email', 'date_of_birth', 'gender',
            'transport_mode', 'vehicle_number', 'previous_shivir', 'gayatri_diksha',
            'education', 'occupation', 'village_taluka', 'country', 'state', 'city',
            'responsibility', 'interested_in_volunteering', 'volunteering_details',
            'volunteer_start_date', 'volunteer_end_date'
        ]
        
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'नाम'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'मोबाइल नं.', 'maxlength': '10'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ईमेल'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'transport_mode': forms.Select(attrs={'class': 'form-select'}, choices=[('', 'परिवहन माध्यम चुनें')] + list(EventRegistration.TRANSPORT_CHOICES)),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'वाहन नंबर'}),
            'previous_shivir': forms.RadioSelect(choices=[(True, 'हाँ'), (False, 'नहीं')], attrs={'class': 'form-check-input'}),
            'education': forms.Select(attrs={'class': 'form-select'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'व्यवसाय'}),
            'village_taluka': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'गांव/तालुका'}),
            'country': forms.HiddenInput(),
            'state': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.Select(attrs={'class': 'form-select'}),


            'responsibility': forms.Select(attrs={'class': 'form-select'}),
            'interested_in_volunteering': forms.RadioSelect(choices=[(True, 'हाँ'), (False, 'नहीं')], attrs={'class': 'form-check-input'}),
            'volunteering_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'आप कैसे योगदान देना चाहते हैं?'}),
            'volunteer_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': '2025-10-12', 'max': '2025-10-30'}),
            'volunteer_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': '2025-10-12', 'max': '2025-10-30'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set country to India by default
        self.fields['country'].initial = 'India'
        
        # Set data if not provided
        if 'data' in kwargs and kwargs['data'] is not None:
            data = kwargs['data'].copy()
            if not data.get('country'):
                data['country'] = 'India'
            kwargs['data'] = data
        
        # Set state choices from CSV
        self.fields['state'].choices = self.get_state_choices()
        self.fields['city'].choices = [('', 'जिला चुनें')]
        
        # Set responsibility choices (only if field exists)
        if 'responsibility' in self.fields:
            responsibility_choices = [('', 'जिम्मेदारी चुनें')]
            responsibility_choices.extend([(r.id, r.name) for r in ResponsibilityOption.objects.filter(is_active=True).order_by('order', 'name')])
            self.fields['responsibility'].choices = responsibility_choices
        
        # Set initial value for campaigns to include mandatory 'युवा जोड़ो अभियान'
        if not self.instance.pk:
            self.fields['campaigns'].initial = ['youth_connect']
        
        # Set vibhag choices (only if field exists)
        if 'vibhags' in self.fields:
            vibhag_choices = [(v.id, v.name) for v in VibhagOption.objects.filter(is_active=True).order_by('order', 'name')]
            self.fields['vibhags'].choices = vibhag_choices
        
        self.fields['occupation'].required = False
    
    def clean_vehicle_number(self):
        transport_mode = self.cleaned_data.get('transport_mode')
        vehicle_number = self.cleaned_data.get('vehicle_number')
        
        if transport_mode == 'car' and not vehicle_number:
            raise forms.ValidationError('कार के लिए वाहन नंबर आवश्यक है।')
        return vehicle_number
    
    def clean_volunteering_details(self):
        interested = self.cleaned_data.get('interested_in_volunteering')
        details = self.cleaned_data.get('volunteering_details')
        
        if interested and not details:
            raise forms.ValidationError('कृपया बताएं कि आप कैसे योगदान देना चाहते हैं।')
        return details
    
    def clean_special_skills_other(self):
        special_skills = self.cleaned_data.get('special_skills', [])
        special_skills_other = self.cleaned_data.get('special_skills_other', '')
        
        if 'other' in special_skills and not special_skills_other.strip():
            raise forms.ValidationError('कृपया अन्य विशेष कौशल का विवरण दें।')
        
        return special_skills_other
    

    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.selected_campaigns = self.cleaned_data.get('campaigns', [])
        instance.special_skills = self.cleaned_data.get('special_skills', [])
        instance.special_skills_other = self.cleaned_data.get('special_skills_other', '')
        instance.selected_vibhags = self.cleaned_data.get('vibhags', [])
        instance.country = 'India'  # Ensure country is always India
        
        # Handle gayatri_diksha conversion
        gayatri_diksha = self.cleaned_data.get('gayatri_diksha')
        if gayatri_diksha is not None:
            instance.gayatri_diksha = gayatri_diksha == 'True' or gayatri_diksha is True
        
        # Handle arrival_date separately
        arrival_date = self.cleaned_data.get('arrival_date')
        if arrival_date:
            from datetime import datetime
            if isinstance(arrival_date, str):
                instance.arrival_date = datetime.strptime(arrival_date, '%Y-%m-%d').date()
            else:
                instance.arrival_date = arrival_date
        
        if commit:
            instance.save()
        return instance


# Participant Registration Form (Regular Registration)
class EventRegistrationForm(BaseEventRegistrationForm):
    # Override arrival_date for normal registration
    arrival_date = forms.ChoiceField(
        choices=EventRegistration.ARRIVAL_DATE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label="आगमन तिथि"
    )
    
    # Document upload fields as URL fields
    aadhar_upload_type = forms.ChoiceField(
        choices=[('full', 'पूरा आधार कार्ड'), ('separate', 'अलग-अलग (आगे-पीछे)')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=False,
        label="आधार कार्ड अपलोड का तरीका"
    )
    
    aadhar_full = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label="पूरा आधार कार्ड"
    )
    
    aadhar_front = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label="आधार कार्ड (आगे)"
    )
    
    aadhar_back = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label="आधार कार्ड (पीछे)"
    )
    
    passport_photo = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label="पासपोर्ट साइज़ फोटो"
    )
    
    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        
        # Age validation only for participant registration
        if date_of_birth:
            from datetime import date
            today = date.today()
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            
            if age < 18:
                raise forms.ValidationError('प्रतिभागी पंजीकरण के लिए आयु 18 वर्ष से कम नहीं होनी चाहिए।')
            elif age > 45:
                raise forms.ValidationError('प्रतिभागी पंजीकरण के लिए आयु 45 वर्ष से अधिक नहीं होनी चाहिए।')
        
        return date_of_birth
    
    class Meta:
        model = EventRegistration
        fields = [
            'full_name', 'phone', 'email', 'date_of_birth', 'gender',
            'transport_mode', 'vehicle_number', 'previous_shivir', 'gayatri_diksha',
            'education', 'occupation', 'village_taluka', 'country', 'state', 'city',
            'arrival_date', 'interested_in_volunteering', 'volunteering_details'
        ]
        
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'नाम'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'मोबाइल नं.', 'maxlength': '10'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ईमेल'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'transport_mode': forms.Select(attrs={'class': 'form-select'}, choices=[('', 'परिवहन माध्यम चुनें')] + list(EventRegistration.TRANSPORT_CHOICES)),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'वाहन नंबर'}),
            'previous_shivir': forms.RadioSelect(choices=[(True, 'हाँ'), (False, 'नहीं')], attrs={'class': 'form-check-input'}),
            'education': forms.Select(attrs={'class': 'form-select'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'व्यवसाय'}),
            'village_taluka': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'गांव/तालुका'}),
            'country': forms.HiddenInput(),
            'state': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'arrival_date': forms.Select(attrs={'class': 'form-select'}),
            'interested_in_volunteering': forms.RadioSelect(choices=[(True, 'हाँ'), (False, 'नहीं')], attrs={'class': 'form-check-input'}),
            'volunteering_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'आप कैसे योगदान देना चाहते हैं?'}),

        }
    
    def clean_campaigns(self):
        campaigns = self.cleaned_data.get('campaigns', [])
        
        # Ensure 'युवा जोड़ो अभियान' is always selected
        if 'youth_connect' not in campaigns:
            campaigns.append('youth_connect')
        
        # Ensure at least one additional campaign is selected
        if len(campaigns) < 2:
            raise forms.ValidationError('कृपया युवा जोड़ो अभियान के अतिरिक्त कम से कम एक और अभियान चुनें।')
        
        return campaigns
    
    def clean(self):
        cleaned_data = super().clean()
        aadhar_type = cleaned_data.get('aadhar_upload_type')
        aadhar_full = cleaned_data.get('aadhar_full')
        aadhar_front = cleaned_data.get('aadhar_front')
        aadhar_back = cleaned_data.get('aadhar_back')
        passport_photo = cleaned_data.get('passport_photo')
        
        # Check if user has uploaded aadhar in any valid way
        has_full_aadhar = bool(aadhar_full and str(aadhar_full).strip())
        has_front_back = bool(aadhar_front and str(aadhar_front).strip() and aadhar_back and str(aadhar_back).strip())
        
        if not has_full_aadhar and not has_front_back:
            raise forms.ValidationError('आधार कार्ड अपलोड करना आवश्यक है (पूरा या आगे-पीछे)।')
        
        # Validate passport photo
        if not passport_photo or not str(passport_photo).strip():
            raise forms.ValidationError('कृपया पासपोर्ट साइज़ फोटो अपलोड करें।')
        
        return cleaned_data


# Volunteer Registration Form
class VolunteerRegistrationForm(BaseEventRegistrationForm):
    def clean_volunteer_start_date(self):
        start_date = self.cleaned_data.get('volunteer_start_date')
        if not start_date:
            raise forms.ValidationError('समयदानी के लिए प्रारंभ तिथि आवश्यक है।')
        return start_date
    
    def clean_volunteer_end_date(self):
        end_date = self.cleaned_data.get('volunteer_end_date')
        start_date = self.cleaned_data.get('volunteer_start_date')
        
        if not end_date:
            raise forms.ValidationError('समयदानी के लिए समाप्ति तिथि आवश्यक है।')
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError('समाप्ति तिथि प्रारंभ तिथि से पहले नहीं हो सकती।')
        
        return end_date
    
    def clean_arrival_date(self):
        arrival_date = self.cleaned_data.get('arrival_date')
        volunteer_start_date = self.cleaned_data.get('volunteer_start_date')
        
        if volunteer_start_date and arrival_date:
            from datetime import datetime, timedelta
            
            # Parse dates
            if isinstance(arrival_date, str):
                arrival_date = datetime.strptime(arrival_date, '%Y-%m-%d').date()
            if isinstance(volunteer_start_date, str):
                volunteer_start_date = datetime.strptime(volunteer_start_date, '%Y-%m-%d').date()
            
            # Check if arrival date is within valid range (up to 2 days before volunteer start)
            min_arrival = volunteer_start_date - timedelta(days=2)
            max_arrival = volunteer_start_date
            
            if not (min_arrival <= arrival_date <= max_arrival):
                raise forms.ValidationError('आगमन तिथि समयदान प्रारंभ से 2 दिन पहले से लेकर समयदान प्रारंभ दिन तक होनी चाहिए।')
        
        return arrival_date
    
    def clean_vibhags(self):
        vibhags = self.cleaned_data.get('vibhags', [])
        if not vibhags:
            raise forms.ValidationError('कृपया कम से कम एक कार्य विभाग चुनें।')
        return vibhags
    
    def clean_campaigns(self):
        campaigns = self.cleaned_data.get('campaigns', [])
        
        # Ensure 'युवा जोड़ो अभियान' is always selected
        if 'youth_connect' not in campaigns:
            campaigns.append('youth_connect')
        
        # Ensure at least one additional campaign is selected
        if len(campaigns) < 2:
            raise forms.ValidationError('कृपया युवा जोड़ो अभियान के अतिरिक्त कम से कम एक और अभियान चुनें।')
        
        return campaigns


# Organization Representative Registration Form
class OrganizationRegistrationForm(BaseEventRegistrationForm):
    # Override arrival_date for organization registration
    arrival_date = forms.ChoiceField(
        choices=EventRegistration.ARRIVAL_DATE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label="आगमन तिथि"
    )
    
    class Meta:
        model = EventRegistration
        fields = [
            'full_name', 'phone', 'email', 'date_of_birth', 'gender',
            'transport_mode', 'vehicle_number', 'previous_shivir',
            'education', 'occupation', 'village_taluka', 'country', 'state', 'city',
            'arrival_date', 'responsibility', 'interested_in_volunteering', 'volunteering_details'
        ]
        
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'नाम'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'मोबाइल नं.', 'maxlength': '10'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ईमेल'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'transport_mode': forms.Select(attrs={'class': 'form-select'}, choices=[('', 'परिवहन माध्यम चुनें')] + list(EventRegistration.TRANSPORT_CHOICES)),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'वाहन नंबर'}),
            'previous_shivir': forms.RadioSelect(choices=[(True, 'हाँ'), (False, 'नहीं')], attrs={'class': 'form-check-input'}),
            'education': forms.Select(attrs={'class': 'form-select'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'व्यवसाय'}),
            'village_taluka': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'गांव/तालुका'}),
            'country': forms.HiddenInput(),
            'state': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'arrival_date': forms.Select(attrs={'class': 'form-select'}),
            'responsibility': forms.Select(attrs={'class': 'form-select'}),
            'interested_in_volunteering': forms.RadioSelect(choices=[(True, 'हाँ'), (False, 'नहीं')], attrs={'class': 'form-check-input'}),
            'volunteering_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'आप कैसे योगदान देना चाहते हैं?'}),
        }
    
    def clean_responsibility(self):
        responsibility = self.cleaned_data.get('responsibility')
        if not responsibility:
            raise forms.ValidationError('संगठन प्रतिनिधि के लिए जिम्मेदारी चुनना आवश्यक है।')
        return responsibility
    
    def clean_campaigns(self):
        campaigns = self.cleaned_data.get('campaigns', [])
        
        # Ensure 'युवा जोड़ो अभियान' is always selected
        if 'youth_connect' not in campaigns:
            campaigns.append('youth_connect')
        
        # Ensure at least one additional campaign is selected
        if len(campaigns) < 2:
            raise forms.ValidationError('कृपया युवा जोड़ो अभियान के अतिरिक्त कम से कम एक और अभियान चुनें।')
        
        return campaigns


