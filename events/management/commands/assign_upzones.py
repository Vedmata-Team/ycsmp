from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import ApprovalUser, UpZone

class Command(BaseCommand):
    help = 'Assign upzones to upzone users'

    def handle(self, *args, **options):
        # Get all upzones and users
        upzones = UpZone.objects.all()
        
        # Create mapping of user to upzone ID
        user_upzone_mapping = {
            'amarkantak_upzone': 12,  # अमरकंटक उपजोन
            'parjhudi_upzone': 11,    # परखुड़ी उपजोन
            'chhindwara_upzone': 10,  # छिंदवाड़ा उपजोन
            'jabalpur_upzone': 9,     # जबलपुर उपजोन
            'tikamgarh_upzone': 8,    # टीकमगढ़ उपजोन
            'guna_upzone': 7,         # गुना उपजोन
            'gwalior_upzone': 6,      # ग्वालियर उपजोन
            'omkareshwar_upzone': 5,  # ओमकारेश्वर उपजोन
            'indore_upzone': 4,       # इंदौर उपजोन
            'ujjain_upzone': 3,       # उज्जैन उपजोन
            'bhopal_upzone': 2,       # भोपाल उपजोन
        }
        
        for username, upzone_id in user_upzone_mapping.items():
            try:
                user = User.objects.get(username=username)
                upzone = UpZone.objects.get(id=upzone_id)
                
                approval_user, created = ApprovalUser.objects.get_or_create(
                    user=user,
                    defaults={
                        'state_code': 'MP',
                        'upzone': upzone,
                        'is_upzone_approver': True,
                        'is_state_approver': False,
                        'is_district_approver': False,
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Assigned {upzone.name} to {username}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'ApprovalUser already exists for {username}')
                    )
                    
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User {username} not found')
                )
            except UpZone.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'UpZone with ID {upzone_id} not found')
                )