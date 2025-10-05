"""
URL configuration for ycs_mp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.template.loader import render_to_string
from events.sitemap_views import sitemap_view
from vehicle_pass.views import vehicle_verify

def robots_txt(request):
    content = render_to_string('robots.txt')
    return HttpResponse(content, content_type='text/plain')

urlpatterns = [
    path('control/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('sitemap.xml', sitemap_view, name='sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots'),
    path('id/', include('ID.urls')),
    path('vehicle-pass/', include('vehicle_pass.urls')),
    path('vehicle-verify/<int:registration_id>/<str:vehicle_number>/', vehicle_verify, name='vehicle_verify_direct'),
    path('', include('events.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
