from django.urls import path
from . import views
from .profile_views import registration_profile
from . import export_views
from . import admin_export_views
from . import document_views
from . import location_views
from . import password_views

app_name = 'events'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('events/', views.events_list, name='list'),
    path('<int:pk>/', views.event_detail, name='detail'),
    path('<int:pk>/register/', views.event_register, name='register_event'),
    path('<int:pk>/volunteer-register/', views.event_volunteer_register, name='volunteer_register_event'),
    path('<int:pk>/organization-register/', views.event_organization_register, name='organization_register_event'),
    path('register/', views.event_register, name='register'),
    path('volunteer-register/', views.event_volunteer_register, name='volunteer_register'),
    path('organization-register/', views.event_organization_register, name='organization_register'),
    path('success/<int:registration_id>/', views.registration_success, name='success'),
    path('pending/<int:registration_id>/', views.pending_approval, name='pending_approval'),
    path('check-status/', views.check_status, name='check_status'),
    path('resend-email/<int:registration_id>/', views.resend_registration_email, name='resend_email'),
    path('test-email/', views.test_email, name='test_email'),
    
    # Document upload URLs
    path('upload-document/', document_views.upload_document, name='upload_document'),
    path('store-temp-user-info/', document_views.store_temp_user_info, name='store_temp_user_info'),
    
    # Export URLs
    path('export/events/', export_views.export_events, name='export_events'),
    path('export/registrations/', export_views.export_registrations, name='export_registrations'),
    path('export/approval-users/', export_views.export_approval_users, name='export_approval_users'),
    path('export/bulk/', export_views.BulkExportView.as_view(), name='bulk_export'),
    
    # Enhanced Admin Export URLs
    path('admin/bulk-export/', admin_export_views.admin_bulk_export, name='admin_bulk_export'),
    path('admin/start-export/', admin_export_views.start_export, name='admin_start_export'),
    path('admin/export-status/<str:export_id>/', admin_export_views.export_status, name='admin_export_status'),
    path('admin/download/<str:filename>/', admin_export_views.download_export, name='admin_download_export'),
    path('admin/quick-stats/', admin_export_views.quick_stats, name='admin_quick_stats'),
    
    # Location API URLs
    path('api/states/', location_views.get_states, name='api_states'),
    path('api/cities/', location_views.get_cities, name='api_cities'),
    path('api/admin-states/', location_views.get_admin_states, name='api_admin_states'),
    path('api/admin-districts/', location_views.get_admin_districts, name='api_admin_districts'),
    
    # Contact page
    path('contact/', views.contact_page, name='contact'),
    
    # Password change URLs
    path('admin/password_change/', password_views.admin_password_change, name='admin_password_change'),
    
    # Profile URL
    path('profile/<str:profile_id>/', registration_profile, name='registration_profile'),
]
