from django.http import JsonResponse
from .models import State, City
from .models_location import StateDistrict

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

def get_admin_districts(request):
    state_name = request.GET.get('state')
    if state_name:
        districts = StateDistrict.objects.filter(state_name=state_name, is_active=True).values_list('district_name', flat=True).distinct()
        return JsonResponse(list(districts), safe=False)
    return JsonResponse([], safe=False)

def get_admin_states(request):
    states = StateDistrict.objects.filter(is_active=True).values_list('state_name', flat=True).distinct()
    return JsonResponse(list(states), safe=False)