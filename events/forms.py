from django import forms
from .models import EventRegistration
import csv
import os
from django.conf import settings


class EventRegistrationForm(forms.ModelForm):
    # Campaign choices as checkboxes
    campaigns = forms.MultipleChoiceField(
        choices=EventRegistration.CAMPAIGN_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
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
            'transport_mode', 'vehicle_number', 'previous_shivir',
            'education', 'occupation', 'village_taluka', 'country', 'state', 'city',
            'arrival_date', 'departure_date',
            'interested_in_volunteering', 'volunteering_details'
        ]
        
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'नाम'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'मोबाइल नं.', 'pattern': '[0-9]{10}'}),
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

            'arrival_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'departure_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'interested_in_volunteering': forms.RadioSelect(choices=[(True, 'हाँ'), (False, 'नहीं')], attrs={'class': 'form-check-input'}),
            'volunteering_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'आप कैसे योगदान देना चाहते हैं?'}),
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
        self.fields['city'].choices = [('', 'जनपद/जिला चुनें')]
        
        # Set initial value for campaigns to include mandatory 'युवा जोड़ो अभियान'
        if not self.instance.pk:
            self.fields['campaigns'].initial = ['youth_connect']
        
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
    
    def clean_campaigns(self):
        campaigns = self.cleaned_data.get('campaigns', [])
        
        # Ensure 'युवा जोड़ो अभियान' is always selected
        if 'youth_connect' not in campaigns:
            campaigns.append('youth_connect')
        
        # Ensure at least one additional campaign is selected
        if len(campaigns) < 2:
            raise forms.ValidationError('कृपया युवा जोड़ो अभियान के अतिरिक्त कम से कम एक और अभियान चुनें।')
        
        return campaigns
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.selected_campaigns = self.cleaned_data.get('campaigns', [])
        instance.special_skills = self.cleaned_data.get('special_skills', [])
        instance.special_skills_other = self.cleaned_data.get('special_skills_other', '')
        instance.country = 'India'  # Ensure country is always India
        if commit:
            instance.save()
        return instance
