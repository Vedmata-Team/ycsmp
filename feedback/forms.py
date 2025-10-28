from django import forms
from .models import FeedbackResponse

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = FeedbackResponse
        fields = [
            'name', 'contact_number', 'state', 'district',
            'accommodation_food', 'sessions_activities', 'discipline_management', 
            'overall_experience', 'cleanliness_facilities', 'staff_helpfulness',
            'time_management', 'technical_facilities',
            'favorite_session', 'suggestions', 'will_join_again', 'inspiration'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'आपका नाम',
                'required': True
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '10 अंकों का मोबाइल नंबर',
                'pattern': '[0-9]{10}',
                'maxlength': '10',
                'required': True
            }),
            'state': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'district': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'accommodation_food': forms.Select(attrs={'class': 'form-select rating-select'}),
            'sessions_activities': forms.Select(attrs={'class': 'form-select rating-select'}),
            'discipline_management': forms.Select(attrs={'class': 'form-select rating-select'}),
            'overall_experience': forms.Select(attrs={'class': 'form-select rating-select'}),
            'cleanliness_facilities': forms.Select(attrs={'class': 'form-select rating-select'}),
            'staff_helpfulness': forms.Select(attrs={'class': 'form-select rating-select'}),
            'time_management': forms.Select(attrs={'class': 'form-select rating-select'}),
            'technical_facilities': forms.Select(attrs={'class': 'form-select rating-select'}),
            'favorite_session': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'कौन सा सत्र आपको सबसे अच्छा लगा?'
            }),
            'suggestions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'भविष्य में सुधार के लिए आपके सुझाव'
            }),
            'will_join_again': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'inspiration': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'एक पंक्ति में बताएं कि यह शिविर कैसे प्रेरणादायक रहा'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get states from existing registrations
        from events.models import EventRegistration
        states = EventRegistration.objects.values_list('state', flat=True).distinct().order_by('state')
        state_choices = [('', 'राज्य चुनें')] + [(state, state) for state in states]
        self.fields['state'].choices = state_choices
        
        # Initial district choices
        self.fields['district'].choices = [('', 'पहले राज्य चुनें')]
        
        # Rating choices
        rating_choices = [('', 'रेटिंग चुनें')] + [(i, f'{i} ⭐') for i in range(1, 6)]
        for field_name in ['accommodation_food', 'sessions_activities', 'discipline_management', 
                          'overall_experience', 'cleanliness_facilities', 'staff_helpfulness',
                          'time_management', 'technical_facilities']:
            self.fields[field_name].choices = rating_choices