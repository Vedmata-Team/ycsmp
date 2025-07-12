from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Count
from django.http import HttpResponse
from django.utils import timezone
from .models import Event, EventRegistration
from .forms import EventRegistrationForm

def homepage(request):
    """Homepage with featured events and quick stats"""
    # Get featured events
    featured_events = Event.objects.filter(is_published=True, is_featured=True).order_by('event_date')[:3]
    
    # Get upcoming events
    upcoming_events = Event.objects.filter(
        is_published=True, 
        event_date__gte=timezone.now()
    ).order_by('event_date')[:6]
    
    # Get statistics
    total_events = Event.objects.filter(is_published=True).count()
    total_registrations = EventRegistration.objects.filter(approval_status='approved').count()
    pending_approvals = EventRegistration.objects.filter(approval_status='pending').count()
    
    # Get categories with event counts
    categories = Event.objects.filter(is_published=True).values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'featured_events': featured_events,
        'upcoming_events': upcoming_events,
        'total_events': total_events,
        'total_registrations': total_registrations,
        'pending_approvals': pending_approvals,
        'categories': categories,
    }
    return render(request, 'events/homepage.html', context)

def events_list(request):
    """Events list view with filtering"""
    events_queryset = Event.objects.filter(is_published=True).order_by('event_date')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        events_queryset = events_queryset.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(venue__icontains=search_query)
        )
    
    # Category filter
    selected_category = request.GET.get('category', '')
    if selected_category:
        events_queryset = events_queryset.filter(category=selected_category)
    
    # District filter
    selected_district = request.GET.get('district', '')
    if selected_district:
        events_queryset = events_queryset.filter(district=selected_district)
    
    # Pagination
    paginator = Paginator(events_queryset, 12)
    page_number = request.GET.get('page')
    events = paginator.get_page(page_number)
    
    # Get filter options
    categories = Event.objects.values_list('category', flat=True).distinct()
    districts = Event.objects.values_list('district', flat=True).distinct()
    
    context = {
        'events': events,
        'categories': categories,
        'districts': districts,
        'search': search_query,
        'selected_category': selected_category,
        'selected_district': selected_district,
    }
    return render(request, 'events/list.html', context)
        
def event_detail(request, pk):
    """Event detail view"""
    event = get_object_or_404(Event, pk=pk, is_published=True)
    
    # Check if registration is still open
    registration_open = timezone.now() < event.registration_deadline
    spots_available = event.available_spots > 0
    
    context = {
        'event': event,
        'registration_open': registration_open,
        'spots_available': spots_available,
    }
    return render(request, 'events/detail.html', context)

def event_register(request, pk=None):
    """Event registration view"""
    event = None
    if pk:
        event = get_object_or_404(Event, pk=pk, is_published=True)
        
        # Check if registration is closed
        if timezone.now() >= event.registration_deadline:
            messages.error(request, 'इस कार्यक्रम के लिए पंजीकरण बंद हो गया है।')
            return redirect('events:detail', pk=pk)
        
        # Check if spots are available
        if event.available_spots <= 0:
            messages.error(request, 'इस कार्यक्रम के लिए सभी स्थान भर गए हैं।')
            return redirect('events:detail', pk=pk)
    
    if request.method == 'POST':
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            if event:
                registration.event = event
            else:
                # General registration - assign to a default event or handle differently
                latest_event = Event.objects.filter(is_published=True).first()
                if latest_event:
                    registration.event = latest_event
                else:
                    messages.error(request, 'कोई सक्रिय कार्यक्रम उपलब्ध नहीं है।')
                    return redirect('events:list')
            
            registration.save()
            messages.success(request, 'आपका पंजीकरण सफलतापूर्वक जमा हो गया है! अप्रूवल के बाद आपको पंजीकरण नंबर मिलेगा।')
            return redirect('events:pending_approval', registration_id=registration.id)
        else:
            messages.error(request, 'कृपया सभी फील्ड सही तरीके से भरें।')
    else:
        form = EventRegistrationForm()
    
    context = {
        'form': form,
        'event': event,
    }
    return render(request, 'events/register_form.html', context)

def registration_success(request, registration_id):
    """Registration success view - only for approved registrations"""
    registration = get_object_or_404(EventRegistration, id=registration_id, approval_status='approved')
    
    context = {
        'registration': registration,
    }
    return render(request, 'events/success.html', context)

def pending_approval(request, registration_id):
    """Pending approval view"""
    registration = get_object_or_404(EventRegistration, id=registration_id)
    
    context = {
        'registration': registration,
    }
    return render(request, 'events/pending.html', context)

def check_status(request):
    """Check registration status by mobile number"""
    registrations = []
    phone = None
    
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        if phone:
            registrations = EventRegistration.objects.filter(phone=phone).order_by('-registration_date')
            if not registrations:
                messages.error(request, 'इस मोबाइल नंबर से कोई पंजीकरण नहीं मिला।')
    
    context = {
        'registrations': registrations,
        'phone': phone,
    }
    return render(request, 'events/check_status.html', context)

def resend_registration_email(request, registration_id):
    """Resend registration details email"""
    if not request.user.is_staff:
        messages.error(request, 'आपको इस कार्य की अनुमति नहीं है।')
        return redirect('admin:events_eventregistration_changelist')
    
    registration = get_object_or_404(EventRegistration, id=registration_id, approval_status='approved')
    
    from .email_utils import send_registration_details_email
    if send_registration_details_email(registration):
        messages.success(request, f'{registration.full_name} को पंजीकरण विवरण ईमेल भेज दिया गया।')
    else:
        messages.error(request, 'ईमेल भेजने में त्रुटि हुई। कृपया पुन: प्रयास करें।')
    
    return redirect('admin:events_eventregistration_change', registration_id)
