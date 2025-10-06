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

def profile_loading(request, profile_id):
    """Show loading page before profile"""
    actual_profile_url = f'/profile/{profile_id}/view/'
    return render(request, 'events/profile_loading.html', {
        'actual_profile_url': actual_profile_url
    })

def registration_profile(request, profile_id):
    """Display registration profile page - optimized"""
    # Extract phone from profile_id for faster lookup
    phone = profile_id.split('_')[0]
    
    # Get all registrations for this phone and find matching profile_id
    registrations = EventRegistration.objects.select_related('event', 'responsibility').filter(phone=phone)
    
    registration = None
    for reg in registrations:
        if generate_profile_url(reg) == profile_id:
            registration = reg
            break
    
    if not registration:
        raise Http404("Registration not found")
    
    # Get vibhag names only if needed
    vibhag_names = []
    if registration.registration_type == 'volunteer' and registration.selected_vibhags:
        vibhag_ids = [int(vid) for vid in registration.selected_vibhags if str(vid).isdigit()]
        if vibhag_ids:
            vibhags = VibhagOption.objects.filter(id__in=vibhag_ids, is_active=True).values_list('name', flat=True)
            vibhag_names = list(vibhags)
    
    # Get campaign names only if needed
    campaign_names = []
    if registration.selected_campaigns:
        campaign_dict = dict(registration.CAMPAIGN_CHOICES)
        campaign_names = [campaign_dict.get(code, code) for code in registration.selected_campaigns]
    
    # Check if user is primary vehicle user
    is_primary_vehicle_user = True
    if registration.vehicle_number:
        from vehicle_pass.views import get_primary_vehicle_user
        primary_user = get_primary_vehicle_user(registration.vehicle_number)
        is_primary_vehicle_user = not primary_user or primary_user.id == registration.id
    
    context = {
        'registration': registration,
        'vibhag_names': vibhag_names,
        'campaign_names': campaign_names,
        'is_primary_vehicle_user': is_primary_vehicle_user,
    }
    
    return render(request, 'events/registration_profile.html', context)