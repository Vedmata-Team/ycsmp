from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create upzone users with staff access'

    def handle(self, *args, **options):
        users_data = [
            ('amarkantak_upzone', 'Amarkantak123#'),
            ('parjhudi_upzone', 'Parjhudi123#'),
            ('chhindwara_upzone', 'Chhindwara123#'),
            ('jabalpur_upzone', 'Jabalpur123#'),
            ('tikamgarh_upzone', 'Tikamgarh123#'),
            ('guna_upzone', 'Guna123#'),
            ('gwalior_upzone', 'Gwalior123#'),
            ('omkareshwar_upzone', 'Omkareshwar123#'),
            ('indore_upzone', 'Indore123#'),
            ('ujjain_upzone', 'Ujjain123#'),
            ('bhopal_upzone', 'Bhopal123#'),
        ]

        for username, password in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'is_staff': True,
                    'is_superuser': False,
                    'is_active': True,
                }
            )
            
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'User already exists: {username}')
                )