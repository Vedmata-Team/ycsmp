from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from .models import Event
from datetime import datetime

def sitemap_view(request):
    """Generate dynamic sitemap for SEO"""
    
    # Get all published events
    events = Event.objects.filter(is_published=True).order_by('-created_at')
    
    # Static URLs
    static_urls = [
        {
            'loc': request.build_absolute_uri('/'),
            'lastmod': timezone.now().strftime('%Y-%m-%d'),
            'changefreq': 'daily',
            'priority': '1.0'
        },
        {
            'loc': request.build_absolute_uri('/events/'),
            'lastmod': timezone.now().strftime('%Y-%m-%d'),
            'changefreq': 'daily',
            'priority': '0.9'
        },
        {
            'loc': request.build_absolute_uri('/register/'),
            'lastmod': timezone.now().strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.8'
        },
        {
            'loc': request.build_absolute_uri('/volunteer-register/'),
            'lastmod': timezone.now().strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.8'
        },
        {
            'loc': request.build_absolute_uri('/organization-register/'),
            'lastmod': timezone.now().strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.8'
        },
        {
            'loc': request.build_absolute_uri('/check-status/'),
            'lastmod': timezone.now().strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.7'
        },
        {
            'loc': request.build_absolute_uri('/contact/'),
            'lastmod': timezone.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.6'
        }
    ]
    
    # Dynamic event URLs
    event_urls = []
    for event in events:
        event_urls.append({
            'loc': request.build_absolute_uri(f'/{event.pk}/'),
            'lastmod': event.updated_at.strftime('%Y-%m-%d') if hasattr(event, 'updated_at') else event.created_at.strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.8'
        })
        
        # Registration URLs for each event
        event_urls.extend([
            {
                'loc': request.build_absolute_uri(f'/{event.pk}/register/'),
                'lastmod': event.created_at.strftime('%Y-%m-%d'),
                'changefreq': 'weekly',
                'priority': '0.7'
            },
            {
                'loc': request.build_absolute_uri(f'/{event.pk}/volunteer-register/'),
                'lastmod': event.created_at.strftime('%Y-%m-%d'),
                'changefreq': 'weekly',
                'priority': '0.7'
            },
            {
                'loc': request.build_absolute_uri(f'/{event.pk}/organization-register/'),
                'lastmod': event.created_at.strftime('%Y-%m-%d'),
                'changefreq': 'weekly',
                'priority': '0.7'
            }
        ])
    
    # Combine all URLs
    all_urls = static_urls + event_urls
    
    # Generate XML
    sitemap_xml = render_to_string('sitemap.xml', {
        'urls': all_urls,
        'domain': request.get_host()
    })
    
    return HttpResponse(sitemap_xml, content_type='application/xml')