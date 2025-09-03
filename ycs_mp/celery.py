import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')

app = Celery('ycs_mp')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    'cleanup-cache-every-hour': {
        'task': 'events.tasks.cleanup_cache_task',
        'schedule': 3600.0,  # Every hour
    },
    'generate-daily-reports': {
        'task': 'events.tasks.generate_registration_reports_async',
        'schedule': 86400.0,  # Every 24 hours
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')