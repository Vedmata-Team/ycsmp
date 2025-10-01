from django.shortcuts import render
from django.http import JsonResponse
from events.models import EventRegistration

def test_id_card(request):
    """Test view to check ID card generation"""
    # Get a sample registration for testing
    registration = EventRegistration.objects.first()
    
    if not registration:
        return JsonResponse({
            'error': 'No registrations found for testing',
            'message': 'Please create at least one registration to test ID card generation'
        })
    
    context = {
        'registration': registration,
        'test_mode': True,
        'id_card_url': f'/id/card/{registration.id}/'
    }
    
    return render(request, 'ID/test_id_card.html', context)