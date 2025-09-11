from django.core.management.base import BaseCommand
from events.models import VibhagOption

class Command(BaseCommand):
    help = 'Create initial vibhag options for volunteer registration'

    def handle(self, *args, **options):
        vibhags = [
            'आवास',
            'भोजनालय', 
            'प्रदर्शनी',
            'प्रचार प्रसार',
            'स्वच्छता',
            'सुरक्षा',
            'जलकल व्यवस्था',
            'चिकित्सा',
            'मीडिया',
            'दीपयज्ञ व्यवस्था',
            'परिवाहन',
            'स्वागत पंजीयन'
        ]
        
        created_count = 0
        for i, vibhag_name in enumerate(vibhags, 1):
            vibhag, created = VibhagOption.objects.get_or_create(
                name=vibhag_name,
                defaults={'order': i * 10, 'is_active': True}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created vibhag: {vibhag_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Vibhag already exists: {vibhag_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new vibhag options')
        )