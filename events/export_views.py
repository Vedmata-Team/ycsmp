from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .models import Event, EventRegistration, ApprovalUser
from .export_utils import ExportManager, EVENT_FIELDS, REGISTRATION_FIELDS, APPROVAL_USER_FIELDS

@staff_member_required
@require_http_methods(["GET"])
def export_events(request):
    format_type = request.GET.get('format', 'csv')
    event_ids = request.GET.getlist('ids')
    
    if event_ids:
        queryset = Event.objects.filter(id__in=event_ids)
    else:
        queryset = Event.objects.all()
    
    if format_type == 'csv':
        return ExportManager.export_to_csv(queryset, 'events_export', EVENT_FIELDS)
    elif format_type == 'excel':
        return ExportManager.export_to_excel(queryset, 'events_export', EVENT_FIELDS)
    elif format_type == 'pdf':
        return ExportManager.export_to_pdf(queryset, 'events_export', EVENT_FIELDS, 'Events Report')

@staff_member_required
@require_http_methods(["GET"])
def export_registrations(request):
    format_type = request.GET.get('format', 'csv')
    registration_ids = request.GET.getlist('ids')
    event_id = request.GET.get('event_id')
    status = request.GET.get('status')
    
    queryset = EventRegistration.objects.all()
    
    if registration_ids:
        queryset = queryset.filter(id__in=registration_ids)
    if event_id:
        queryset = queryset.filter(event_id=event_id)
    if status:
        queryset = queryset.filter(approval_status=status)
    
    if format_type == 'csv':
        return ExportManager.export_to_csv(queryset, 'registrations_export', REGISTRATION_FIELDS)
    elif format_type == 'excel':
        return ExportManager.export_to_excel(queryset, 'registrations_export', REGISTRATION_FIELDS)
    elif format_type == 'pdf':
        return ExportManager.export_to_pdf(queryset, 'registrations_export', REGISTRATION_FIELDS, 'Registrations Report')

@staff_member_required
@require_http_methods(["GET"])
def export_approval_users(request):
    format_type = request.GET.get('format', 'csv')
    user_ids = request.GET.getlist('ids')
    
    if user_ids:
        queryset = ApprovalUser.objects.filter(id__in=user_ids)
    else:
        queryset = ApprovalUser.objects.all()
    
    if format_type == 'csv':
        return ExportManager.export_to_csv(queryset, 'approval_users_export', APPROVAL_USER_FIELDS)
    elif format_type == 'excel':
        return ExportManager.export_to_excel(queryset, 'approval_users_export', APPROVAL_USER_FIELDS)
    elif format_type == 'pdf':
        return ExportManager.export_to_pdf(queryset, 'approval_users_export', APPROVAL_USER_FIELDS, 'Approval Users Report')

@method_decorator(staff_member_required, name='dispatch')
class BulkExportView(View):
    def get(self, request):
        return render(request, 'admin/bulk_export.html', {
            'events_count': Event.objects.count(),
            'registrations_count': EventRegistration.objects.count(),
            'approval_users_count': ApprovalUser.objects.count(),
        })
    
    def post(self, request):
        export_type = request.POST.get('export_type')
        format_type = request.POST.get('format')
        
        if export_type == 'events':
            queryset = Event.objects.all()
            fields = EVENT_FIELDS
            filename = 'all_events_export'
            title = 'All Events Report'
        elif export_type == 'registrations':
            queryset = EventRegistration.objects.all()
            fields = REGISTRATION_FIELDS
            filename = 'all_registrations_export'
            title = 'All Registrations Report'
        elif export_type == 'approval_users':
            queryset = ApprovalUser.objects.all()
            fields = APPROVAL_USER_FIELDS
            filename = 'all_approval_users_export'
            title = 'All Approval Users Report'
        else:
            return JsonResponse({'error': 'Invalid export type'}, status=400)
        
        if format_type == 'csv':
            return ExportManager.export_to_csv(queryset, filename, fields)
        elif format_type == 'excel':
            return ExportManager.export_to_excel(queryset, filename, fields)
        elif format_type == 'pdf':
            return ExportManager.export_to_pdf(queryset, filename, fields, title)
        else:
            return JsonResponse({'error': 'Invalid format'}, status=400)