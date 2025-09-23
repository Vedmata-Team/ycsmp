from django.http import JsonResponse
from .models import State, City

def get_states(request):
    """Get all states for India"""
    states = State.objects.filter(country__code='IN').values('id', 'name', 'code')
    return JsonResponse({'states': list(states)})

def get_cities(request):
    """Get cities for a specific state or all cities"""
    state_id = request.GET.get('state_id')
    if state_id:
        cities = City.objects.filter(state_id=state_id).values('id', 'name', 'state_id')
    else:
        cities = City.objects.all().values('id', 'name', 'state_id')
    return JsonResponse({'cities': list(cities)})