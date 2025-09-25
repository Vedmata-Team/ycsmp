from django import forms
from .models_location import StateDistrict

class StateDistrictWidget(forms.MultiWidget):
    """Widget for selecting state and district from admin-managed data"""
    
    def __init__(self, attrs=None):
        widgets = [
            forms.Select(attrs={'class': 'form-control state-select'}),
            forms.Select(attrs={'class': 'form-control district-select'}),
        ]
        super().__init__(widgets, attrs)
    
    def decompress(self, value):
        if value:
            parts = value.split('|') if '|' in str(value) else [value, '']
            return parts if len(parts) == 2 else [parts[0], '']
        return ['', '']
    
    def format_output(self, rendered_widgets):
        return f'''
        <div class="row">
            <div class="col-md-6">
                <label>राज्य:</label>
                {rendered_widgets[0]}
            </div>
            <div class="col-md-6">
                <label>जिला:</label>
                {rendered_widgets[1]}
            </div>
        </div>
        '''

class StateDistrictField(forms.MultiValueField):
    """Field for state-district selection"""
    
    def __init__(self, *args, **kwargs):
        fields = [
            forms.ChoiceField(choices=self.get_state_choices()),
            forms.ChoiceField(choices=[]),
        ]
        super().__init__(fields, *args, **kwargs)
        self.widget = StateDistrictWidget()
    
    def get_state_choices(self):
        states = StateDistrict.objects.filter(is_active=True).values_list('state_name', flat=True).distinct()
        return [('', 'राज्य चुनें')] + [(state, state) for state in states]
    
    def compress(self, data_list):
        if data_list:
            return '|'.join(data_list)
        return ''