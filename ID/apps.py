from django.apps import AppConfig

class IdConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ID'
    verbose_name = 'ID Card Generator'
    
    def ready(self):
        # Import admin customizations when app is ready
        try:
            from . import admin
        except ImportError:
            pass