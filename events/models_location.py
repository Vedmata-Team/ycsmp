from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class StateDistrict(models.Model):
    """Admin-editable states and districts"""
    state_name = models.CharField(max_length=100, verbose_name="राज्य नाम")
    state_code = models.CharField(max_length=10, verbose_name="राज्य कोड")
    district_name = models.CharField(max_length=100, verbose_name="जिला नाम")
    is_active = models.BooleanField(default=True, verbose_name="सक्रिय")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "राज्य-जिला"
        verbose_name_plural = "राज्य-जिले"
        unique_together = ['state_code', 'district_name']
        ordering = ['state_name', 'district_name']
    
    def __str__(self):
        return f"{self.state_name} - {self.district_name}"

@receiver([post_save, post_delete], sender=StateDistrict)
def update_registrations_on_location_change(sender, instance, **kwargs):
    """Auto-update registrations when location data changes"""
    from .models import EventRegistration
    
    if kwargs.get('created', False) or kwargs.get('signal') == post_delete:
        return
    
    # Update existing registrations with old state/district names
    EventRegistration.objects.filter(
        state__iexact=instance.state_name,
        city__iexact=instance.district_name
    ).update(
        state=instance.state_name,
        city=instance.district_name
    )