from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

# This file can be used to add admin customizations for ID card generation
# Currently, we'll add ID card generation links to the EventRegistration admin

def add_id_card_link_to_registration_admin():
    """Add ID card generation link to EventRegistration admin"""
    from events.admin import EventRegistrationAdmin
    from events.models import EventRegistration
    
    # Add ID card link to list display
    original_list_display = list(EventRegistrationAdmin.list_display)
    if 'id_card_link' not in original_list_display:
        original_list_display.append('id_card_link')
        EventRegistrationAdmin.list_display = tuple(original_list_display)
    
    # Add method to generate ID card link
    def id_card_link(self, obj):
        if obj.pk:
            url = reverse('ID:generate_card', args=[obj.pk])
            return format_html(
                '<a href="{}" target="_blank" class="button">🆔 ID कार्ड</a>',
                url
            )
        return "-"
    
    id_card_link.short_description = "ID कार्ड"
    id_card_link.allow_tags = True
    
    # Add the method to the admin class
    EventRegistrationAdmin.id_card_link = id_card_link

# Call the function to add ID card link
add_id_card_link_to_registration_admin()