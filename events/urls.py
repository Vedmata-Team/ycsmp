from django.urls import path
from . import views
from . import export_views

app_name = 'events'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('events/', views.events_list, name='list'),
    path('<int:pk>/', views.event_detail, name='detail'),
    path('<int:pk>/register/', views.event_register, name='register_event'),
    path('register/', views.event_register, name='register'),
    path('success/<int:registration_id>/', views.registration_success, name='success'),
    path('pending/<int:registration_id>/', views.pending_approval, name='pending_approval'),
    path('check-status/', views.check_status, name='check_status'),
    path('resend-email/<int:registration_id>/', views.resend_registration_email, name='resend_email'),
    
    # Export URLs
    path('export/events/', export_views.export_events, name='export_events'),
    path('export/registrations/', export_views.export_registrations, name='export_registrations'),
    path('export/approval-users/', export_views.export_approval_users, name='export_approval_users'),
    path('export/bulk/', export_views.BulkExportView.as_view(), name='bulk_export'),
]
