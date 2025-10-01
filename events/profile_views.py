# events/profile_views.py
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import EventRegistration, VibhagOption


def generate_profile_url(registration):
    """Generate unique URL for registration profile"""
    # Clean name: replace spaces with underscores, remove special chars
    clean_name = registration.full_name.replace(' ', '_').replace('-', '_')
    clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
    
    return f"{registration.phone}_{clean_name}"

def registration_profile(request, profile_id):
    """Display registration profile page"""
    # Find registration by matching profile_id
    registrations = EventRegistration.objects.select_related('event', 'responsibility')
    
    registration = None
    for reg in registrations:
        if generate_profile_url(reg) == profile_id:
            registration = reg
            break
    
    if not registration:
        raise Http404("Registration not found")
    
    # Get vibhag names for volunteers
    vibhag_names = []
    if registration.registration_type == 'volunteer' and registration.selected_vibhags:
        try:
            vibhag_ids = [int(vid) for vid in registration.selected_vibhags if str(vid).isdigit()]
            vibhags = VibhagOption.objects.filter(id__in=vibhag_ids, is_active=True)
            vibhag_names = [v.name for v in vibhags]
        except:
            pass
    
    # Get campaign names
    campaign_names = []
    if registration.selected_campaigns:
        campaign_dict = dict(registration.CAMPAIGN_CHOICES)
        campaign_names = [campaign_dict.get(code, code) for code in registration.selected_campaigns]
    
    context = {
        'registration': registration,
        'vibhag_names': vibhag_names,
        'campaign_names': campaign_names,
        'venue_location': 'https://maps.google.com/maps?q=Shantikunj,+Haridwar',  # Default venue
    }
    
    return render(request, 'events/registration_profile.html', context)