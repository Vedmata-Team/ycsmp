from django.urls import path
from . import views

app_name = 'vehicle_pass'

urlpatterns = [
    path('generate/<int:registration_id>/<str:vehicle_number>/', views.generate_vehicle_pass, name='generate'),
    path('preview/<int:registration_id>/<str:vehicle_number>/', views.vehicle_pass_preview, name='preview'),
]

# Add verification URLs with different base path
from django.urls import path, re_path

# Additional patterns for verification (accessible via /vehicle-pass/verify/)
verify_patterns = [
    re_path(r'^verify/(?P<registration_id>\d+)/(?P<vehicle_number>[^/]+)/$', views.vehicle_verify, name='verify'),
]

urlpatterns += verify_patterns