from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Count, F
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction
from .models import Event, EventRegistration
from .forms import EventRegistrationForm, VolunteerRegistrationForm, OrganizationRegistrationForm
from .email_utils import send_registration_approval_email
import logging

logger = logging.getLogger(__name__)

def homepage(request):
    """Homepage with featured events and quick stats - Optimized"""
    # Optimized queries with select_related
    featured_events = Event.objects.select_related().filter(
        is_published=True, is_featured=True
    ).order_by('event_date')[:3]
    
    upcoming_events = Event.objects.select_related().filter(
        is_published=True, 
        event_date__gte=timezone.now()
    ).order_by('event_date')[:6]
    
    # Use aggregation for better performance
    stats = Event.objects.filter(is_published=True).aggregate(
        total_events=Count('id'),
        categories_count=Count('category', distinct=True)
    )
    
    registration_stats = EventRegistration.objects.aggregate(
        total_registrations=Count('id', filter=Q(approval_status='approved')),
        pending_approvals=Count('id', filter=Q(approval_status='pending'))
    )
    
    # Get categories with event counts
    categories = Event.objects.filter(is_published=True).values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'featured_events': featured_events,
        'upcoming_events': upcoming_events,
        'total_events': stats['total_events'],
        'total_registrations': registration_stats['total_registrations'],
        'pending_approvals': registration_stats['pending_approvals'],
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

def event_organization_register(request, pk=None):
    """Organization representative registration view - CLOSED"""
    event = None
    if pk:
        event = get_object_or_404(Event, pk=pk, is_published=True)
    
    context = {
        'registration_type': 'organization',
        'event': event,
    }
    return render(request, 'events/registration_closed.html', context)


def event_volunteer_register(request, pk=None):
    """Volunteer registration view - CLOSED"""
    event = None
    if pk:
        event = get_object_or_404(Event, pk=pk, is_published=True)
    
    context = {
        'registration_type': 'volunteer',
        'event': event,
    }
    return render(request, 'events/registration_closed.html', context)


def event_register(request, pk=None):
    """Event registration view - CLOSED"""
    event = None
    if pk:
        event = get_object_or_404(Event, pk=pk, is_published=True)
    
    context = {
        'registration_type': 'participant',
        'event': event,
    }
    return render(request, 'events/registration_closed.html', context)
    
    if request.method == 'POST':
        print("\n=== FORM SUBMISSION DEBUG ===")
        print(f"POST request received at {timezone.now()}")
        print(f"Request method: {request.method}")
        print(f"Content type: {request.content_type}")
        print(f"POST data keys: {list(request.POST.keys())}")
        
        # Log all form data
        print("\n--- FORM DATA ---")
        for key, value in request.POST.items():
            if isinstance(value, list):
                print(f"{key}: {value}")
            else:
                print(f"{key}: {value}")
        
        form = EventRegistrationForm(request.POST)
        print(f"\nForm created: {form.__class__.__name__}")
        print(f"Form is bound: {form.is_bound}")
        print(f"Form is valid: {form.is_valid()}")
        
        if not form.is_valid():
            print("\n--- FORM VALIDATION ERRORS ---")
            for field, errors in form.errors.items():
                print(f"{field}: {errors}")
            if form.non_field_errors():
                print(f"Non-field errors: {form.non_field_errors()}")
        
        if form.is_valid():
            try:
                print("\n--- STARTING TRANSACTION ---")
                with transaction.atomic():
                    print("Inside transaction block")
                    print("Allowing multiple registrations from same user")
                    
                    print("Creating registration")
                    registration = form.save(commit=False)
                    print("Registration object created (without event yet)")
                    registration.registration_type = 'participant'
                    print(f"Registration type set: {registration.registration_type}")
                    
                    # Handle campaigns and special skills from POST data
                    campaigns = request.POST.getlist('campaigns')
                    special_skills = request.POST.getlist('special_skills')
                    special_skills_other = request.POST.get('special_skills_other', '')
                    print(f"Campaigns: {campaigns}")
                    print(f"Special skills: {special_skills}")
                    print(f"Special skills other: {special_skills_other}")
                    
                    registration.selected_campaigns = campaigns
                    registration.special_skills = special_skills
                    registration.special_skills_other = special_skills_other
                    print("Campaign and skills data set")
                    
                    # Save document URLs to registration object
                    aadhar_type = request.POST.get('aadhar_upload_type')
                    aadhar_full = request.POST.get('aadhar_full')
                    aadhar_front = request.POST.get('aadhar_front')
                    aadhar_back = request.POST.get('aadhar_back')
                    passport_photo = request.POST.get('passport_photo')
                    
                    registration.aadhar_upload_type = aadhar_type
                    registration.aadhar_full = aadhar_full if aadhar_full and aadhar_full.strip() else None
                    registration.aadhar_front = aadhar_front if aadhar_front and aadhar_front.strip() else None
                    registration.aadhar_back = aadhar_back if aadhar_back and aadhar_back.strip() else None
                    registration.passport_photo = passport_photo if passport_photo and passport_photo.strip() else None
                    
                    if event:
                        registration.event = event
                    else:
                        latest_event = Event.objects.filter(is_published=True).first()
                        if latest_event:
                            registration.event = latest_event
                        else:
                            messages.error(request, 'कोई सक्रिय कार्यक्रम उपलब्ध नहीं है।')
                            return redirect('events:list')
                    
                    registration.save()
                    
                    messages.info(request, 'आपका पंजीकरण जमा हो गया है और अप्रूवल की प्रक्रिया में है। कृपया नीचे दिए गए निर्देशों को ध्यान से पढ़ें।')
                    return redirect('events:pending_approval', registration_id=registration.id)
                    
            except Exception as e:
                print(f"\n--- REGISTRATION ERROR ---")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                logger.error(f"Registration failed: {str(e)}")
                messages.error(request, 'पंजीकरण में त्रुटि हुई। कृपया पुन: प्रयास करें।')
        else:
            print(f"\n--- FORM VALIDATION FAILED ---")
            print(f"Returning form with errors to template")
            logger.error(f"Form validation failed: {form.errors}")
            messages.error(request, 'कृपया सभी फील्ड सही तरीके से भरें।')
    else:
        print(f"\n=== GET REQUEST ===")
        print(f"Request method: {request.method}")
        print(f"Creating new form instance")
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
    """Check registration status by mobile number with profile links"""
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
    


def test_email(request):
    """Test email configuration"""
    if not request.user.is_staff:
        return HttpResponse('Unauthorized', status=401)
    
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        print("\n=== EMAIL TEST DEBUG ===")
        print(f"SMTP Host: {settings.EMAIL_HOST}")
        print(f"SMTP Port: {settings.EMAIL_PORT}")
        print(f"Use TLS: {settings.EMAIL_USE_TLS}")
        print(f"From email: {settings.DEFAULT_FROM_EMAIL}")
        print(f"Host user: {settings.EMAIL_HOST_USER}")
        
        send_mail(
            subject='Test Email - YCS MP',
            message='This is a test email to verify SMTP configuration.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],  # Change this to your email for testing
            fail_silently=False,
        )
        return HttpResponse('Test email sent successfully! Check console for debug info.')
    except Exception as e:
        print(f"Test email failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return HttpResponse(f'Test email failed: {str(e)}')

def contact_page(request):
    return render(request, 'contact.html')