from django.contrib.admin import SimpleListFilter
from django.db import models

class UpZoneFilter(SimpleListFilter):
    title = 'उपजोन'
    parameter_name = 'upzone'

    def lookups(self, request, model_admin):
        from .models import UpZone
        upzones = UpZone.objects.filter(is_active=True)
        return [(upzone.id, upzone.name) for upzone in upzones]

    def queryset(self, request, queryset):
        if self.value():
            from .models import UpZone
            try:
                upzone = UpZone.objects.get(id=self.value())
                if upzone.districts:
                    return queryset.filter(city__in=upzone.districts)
            except UpZone.DoesNotExist:
                pass
        return queryset

class RegistrationNumberFilter(SimpleListFilter):
    title = 'Registration Number Status'
    parameter_name = 'has_registration_number'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Has Registration Number'),
            ('no', 'No Registration Number'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(registration_number__isnull=False).exclude(registration_number='')
        elif self.value() == 'no':
            return queryset.filter(models.Q(registration_number__isnull=True) | models.Q(registration_number=''))
        return queryset