from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from django.db import models
from datetime import datetime, timedelta
import uuid
import os
from .models import Event, EventRegistration, ApprovalUser, ResponsibilityOption, VibhagOption
from .fast_export import export_manager

@staff_member_required
def admin_bulk_export(request):
    """Enhanced bulk export with filters for admin"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Only superusers can access bulk export.')
        return render(request, 'admin/access_denied.html')
    
    context = {
        'title': 'Bulk Export with Filters',
        'events': Event.objects.all().order_by('-created_at'),
        'approval_statuses': EventRegistration._meta.get_field('approval_status').choices,
        'registration_types': EventRegistration._meta.get_field('registration_type').choices,
        'states': EventRegistration.objects.values_list('state', flat=True).distinct().order_by('state'),
        'cities': EventRegistration.objects.values_list('city', flat=True).distinct().order_by('city'),
        'total_registrations': EventRegistration.objects.count(),
        'approved_registrations': EventRegistration.objects.filter(approval_status='approved').count(),
        'pending_registrations': EventRegistration.objects.filter(approval_status='pending').count(),
    }
    
    return render(request, 'admin/enhanced_bulk_export.html', context)

@staff_member_required
@require_http_methods(["POST"])
def start_export(request):
    """Start async export with filters"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get filters from request
    filters = {}
    if request.POST.get('approval_status'):
        filters['approval_status'] = request.POST.get('approval_status')
    if request.POST.get('state'):
        filters['state'] = request.POST.get('state')
    if request.POST.get('city'):
        filters['city'] = request.POST.get('city')
    if request.POST.get('registration_type'):
        filters['registration_type'] = request.POST.get('registration_type')
    if request.POST.get('event_id'):
        filters['event_id'] = request.POST.get('event_id')
    if request.POST.get('date_from'):
        filters['date_from'] = request.POST.get('date_from')
    if request.POST.get('date_to'):
        filters['date_to'] = request.POST.get('date_to')
    
    # Generate unique export ID
    export_id = str(uuid.uuid4())
    
    # Start export
    export_manager.start_export(export_id, filters)
    
    return JsonResponse({
        'export_id': export_id,
        'message': 'Export started successfully'
    })

@staff_member_required
@require_http_methods(["GET"])
def export_status(request, export_id):
    """Check export status"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    status = export_manager.get_export_status(export_id)
    return JsonResponse(status)

@staff_member_required
@require_http_methods(["GET"])
def download_export(request, filename):
    """Download exported file"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    filepath = os.path.join('exports', filename)
    
    if not os.path.exists(filepath):
        raise Http404("Export file not found")
    
    with open(filepath, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

@staff_member_required
@require_http_methods(["GET"])
def quick_stats(request):
    """Get quick statistics for dashboard"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'total_registrations': EventRegistration.objects.count(),
        'approved_registrations': EventRegistration.objects.filter(approval_status='approved').count(),
        'pending_registrations': EventRegistration.objects.filter(approval_status='pending').count(),
        'rejected_registrations': EventRegistration.objects.filter(approval_status='rejected').count(),
        'this_week': EventRegistration.objects.filter(registration_date__gte=week_ago).count(),
        'this_month': EventRegistration.objects.filter(registration_date__gte=month_ago).count(),
        'by_state': list(EventRegistration.objects.values('state').annotate(
            count=models.Count('id')
        ).order_by('-count')[:10]),
        'by_registration_type': list(EventRegistration.objects.values('registration_type').annotate(
            count=models.Count('id')
        )),
        'recent_exports': []  # Could track recent exports if needed
    }
    
    return JsonResponse(stats)