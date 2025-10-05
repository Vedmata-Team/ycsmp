from django.urls import path
from . import views

app_name = 'vehicle_pass'

urlpatterns = [
    path('generate/<int:registration_id>/<str:vehicle_number>/', views.generate_vehicle_pass, name='generate'),
    path('preview/<int:registration_id>/<str:vehicle_number>/', views.vehicle_pass_preview, name='preview'),
    path('verify/<int:registration_id>/<str:vehicle_number>/', views.vehicle_verify, name='verify'),
]