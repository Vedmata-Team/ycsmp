from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.core.cache import cache
from django.utils import timezone
from .models import FeedbackResponse
from .forms import FeedbackForm
import json
import hashlib
import time
import logging

logger = logging.getLogger(__name__)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@never_cache
@csrf_protect
def feedback_form(request):
    # Cache states for 1 hour to reduce DB load
    states = cache.get('feedback_states')
    if not states:
        try:
            from events.models_location import StateDistrict
            states = list(StateDistrict.objects.filter(is_active=True).values_list('state_name', flat=True).distinct().order_by('state_name'))
            cache.set('feedback_states', states, 3600)  # 1 hour cache
        except:
            states = []
    
    # Rating fields configuration
    ratings = [
        {'name': 'accommodation_food', 'label': 'आवास और भोजन'},
        {'name': 'sessions_activities', 'label': 'सत्र और गतिविधियां'},
        {'name': 'discipline_management', 'label': 'अनुशासन और प्रबंधन'},
        {'name': 'overall_experience', 'label': 'समग्र अनुभव'},
        {'name': 'cleanliness_facilities', 'label': 'स्वच्छता और सुविधाएं'},
        {'name': 'staff_helpfulness', 'label': 'स्टाफ की सहायता'},
        {'name': 'time_management', 'label': 'समय प्रबंधन'},
        {'name': 'technical_facilities', 'label': 'तकनीकी सुविधाएं'},
    ]
    
    if request.method == 'POST':
        # Rate limiting per IP
        client_ip = get_client_ip(request)
        rate_key = f'feedback_rate_{client_ip}'
        
        if cache.get(rate_key, 0) >= 3:  # Max 3 submissions per hour per IP
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'बहुत अधिक प्रयास। कृपया 1 घंटे बाद पुनः प्रयास करें।'
                })
            messages.error(request, 'बहुत अधिक प्रयास। कृपया 1 घंटे बाद पुनः प्रयास करें।')
            return redirect('feedback_form')
        
        # Duplicate prevention using phone + timestamp hash
        phone = request.POST.get('phone', '')
        if phone:
            duplicate_key = f'feedback_dup_{hashlib.md5(phone.encode()).hexdigest()}'
            if cache.get(duplicate_key):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'इस नंबर से पहले से प्रतिक्रिया जमा की गई है।'
                    })
                messages.error(request, 'इस नंबर से पहले से प्रतिक्रिया जमा की गई है।')
                return redirect('feedback_form')
        
        form = FeedbackForm(request.POST)
        if form.is_valid():
            try:
                # Use select_for_update to prevent race conditions
                with transaction.atomic():
                    feedback = form.save(commit=False)
                    feedback.ip_address = client_ip
                    feedback.created_at = timezone.now()
                    feedback.save()
                
                # Set rate limiting and duplicate prevention
                cache.set(rate_key, cache.get(rate_key, 0) + 1, 3600)  # 1 hour
                if phone:
                    cache.set(duplicate_key, True, 86400)  # 24 hours
                
                logger.info(f'Feedback saved successfully for {phone}')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'आपकी प्रतिक्रिया सफलतापूर्वक सहेजी गई! धन्यवाद 🙏',
                        'redirect_url': f'/feedback/success/?name={feedback.name}'
                    })
                
                return redirect(f'/feedback/success/?name={feedback.name}')
                
            except IntegrityError as e:
                logger.error(f'Integrity error in feedback: {e}')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'डुप्लिकेट डेटा। कृपया पुनः प्रयास करें।'
                    })
                messages.error(request, 'डुप्लिकेट डेटा। कृपया पुनः प्रयास करें।')
            except Exception as e:
                logger.error(f'Error saving feedback: {e}')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'सर्वर व्यस्त है। कृपया कुछ सेकंड बाद पुनः प्रयास करें।'
                    })
                messages.error(request, 'सर्वर व्यस्त है। कृपया कुछ सेकंड बाद पुनः प्रयास करें।')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                    'message': 'कृपया सभी आवश्यक फ़ील्ड भरें।'
                })
    else:
        form = FeedbackForm()
    
    context = {
        'form': form,
        'states': states,
        'ratings': ratings,
    }
    return render(request, 'feedback/feedback_form.html', context)

def feedback_success(request):
    name = request.GET.get('name', 'मित्र')  # Default to 'मित्र' if no name
    context = {
        'user_name': name
    }
    return render(request, 'feedback/success.html', context)



def submit_feedback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create feedback instance
            feedback = FeedbackResponse(
                name=data.get('name'),
                contact_number=data.get('contact_number'),
                state=data.get('state'),
                district=data.get('district'),
                accommodation_food=int(data.get('accommodation_food')),
                sessions_activities=int(data.get('sessions_activities')),
                discipline_management=int(data.get('discipline_management')),
                overall_experience=int(data.get('overall_experience')),
                cleanliness_facilities=int(data.get('cleanliness_facilities')),
                staff_helpfulness=int(data.get('staff_helpfulness')),
                time_management=int(data.get('time_management')),
                technical_facilities=int(data.get('technical_facilities')),
                favorite_session=data.get('favorite_session', ''),
                suggestions=data.get('suggestions', ''),
                will_join_again=data.get('will_join_again') == 'true',
                inspiration=data.get('inspiration', ''),
                ip_address=get_client_ip(request)
            )
            
            feedback.save()
            
            return JsonResponse({
                'success': True,
                'message': 'धन्यवाद! रीडायरेक्ट किया जा रहा है...',
                'redirect_url': f'/feedback/success/?name={data.get("name", "मित्र")}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'कुछ त्रुटि हुई। कृपया पुनः प्रयास करें।'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=405)