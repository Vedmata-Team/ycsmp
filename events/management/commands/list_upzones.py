from django.core.management.base import BaseCommand
from events.models import UpZone

class Command(BaseCommand):
    help = 'List all upzones'

    def handle(self, *args, **options):
        upzones = UpZone.objects.all()
        
        self.stdout.write("Available UpZones:")
        for upzone in upzones:
            self.stdout.write(f"ID: {upzone.id}, Name: {upzone.name}")