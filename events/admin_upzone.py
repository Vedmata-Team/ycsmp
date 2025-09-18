from django.contrib import admin
from django import forms
from django.conf import settings
import csv
import os
from .models import UpZone

class UpZoneAdminForm(forms.ModelForm):
    districts = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={
            'class': 'mp-districts-select',
            'size': '15',
            'style': 'width: 100%; height: 300px;'
        }),
        required=False,
        label="जिले",
        help_text="Search करके जिले ढूंढें, फिर Ctrl+Click से multiple select करें"
    )
    
    class Meta:
        model = UpZone
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get MP districts
        try:
            csv_path = os.path.join(settings.STATICFILES_DIRS[0], 'csv', 'cities.csv')
            districts = set()
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get('state_code') == 'MP':
                        districts.add(row['name'])
            self.fields['districts'].choices = [(d, d) for d in sorted(districts)]
        except:
            self.fields['districts'].choices = []
        
        if self.instance.pk and self.instance.districts:
            self.fields['districts'].initial = self.instance.districts
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.districts = self.cleaned_data['districts']
        if commit:
            instance.save()
        return instance

@admin.register(UpZone)
class UpZoneAdmin(admin.ModelAdmin):
    form = UpZoneAdminForm
    list_display = ('name', 'get_districts_display', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    list_editable = ('is_active',)
    
    fieldsets = (
        ('उपजोन जानकारी', {
            'fields': ('name', 'districts', 'is_active')
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/upzone_admin.css',)
        }
        js = ('admin/js/upzone_search.js',)
    
    def get_districts_display(self, obj):
        return obj.get_districts_display()
    get_districts_display.short_description = 'जिले'