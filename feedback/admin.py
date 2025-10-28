from django.contrib import admin
from django.db.models import Avg
from django.utils.html import format_html
from .models import FeedbackResponse

@admin.register(FeedbackResponse)
class FeedbackResponseAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'district', 'overall_experience_stars', 'created_at']
    list_filter = ['state', 'district', 'created_at', 'will_join_again']
    search_fields = ['name', 'contact_number', 'state', 'district']
    readonly_fields = ['submission_id', 'created_at', 'ip_address']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'contact_number', 'state', 'district')
        }),
        ('Ratings', {
            'fields': (
                'accommodation_food', 'sessions_activities',
                'discipline_management', 'overall_experience',
                'cleanliness_facilities', 'staff_helpfulness',
                'time_management', 'technical_facilities'
            )
        }),
        ('Feedback', {
            'fields': ('favorite_session', 'suggestions', 'will_join_again', 'inspiration')
        }),
        ('Metadata', {
            'fields': ('submission_id', 'created_at', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    
    def overall_experience_stars(self, obj):
        stars = '⭐' * obj.overall_experience
        return format_html(f'<span style="font-size: 1.2em;">{stars}</span>')
    overall_experience_stars.short_description = 'Overall Experience'
    
    def changelist_view(self, request, extra_context=None):
        # Add statistics to the change list view
        response = super().changelist_view(request, extra_context)
        
        try:
            qs = self.get_queryset(request)
            stats = {
                'total_responses': qs.count(),
                'avg_overall': qs.aggregate(Avg('overall_experience'))['overall_experience__avg'],
                'will_join_again': qs.filter(will_join_again=True).count(),
            }
            
            if not extra_context:
                extra_context = {}
            extra_context.update(stats)
            response.context_data.update(extra_context)
        except (AttributeError, KeyError):
            pass
        
        return response
    
    def has_delete_permission(self, request, obj=None):
        # Allow deletion for superusers
        return request.user.is_superuser