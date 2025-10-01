from django.urls import path
from . import views, test_views, preview_views

app_name = 'ID'

urlpatterns = [
    path('card/<int:registration_id>/', views.generate_id_card, name='generate_card'),
    path('preview/<int:registration_id>/', preview_views.preview_id_card, name='preview_card'),
    path('test/', test_views.test_id_card, name='test_card'),
]