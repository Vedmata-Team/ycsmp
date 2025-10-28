from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('', views.feedback_form, name='form'),
    path('submit/', views.submit_feedback, name='submit'),
    path('success/', views.feedback_success, name='success'),
]