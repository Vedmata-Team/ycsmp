from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import UpZone, ApprovalUser

class Command(BaseCommand):
    help = 'Setup UpZones for MP districts and create UpZone approvers'

    def add_arguments(self, parser):
        parser.add_argument('--create-sample', action='store_true', help='Create sample UpZones')
        parser.add_argument('--create-upzone', type=str, help='Create UpZone with name')
        parser.add_argument('--districts', nargs='+', help='Districts for the UpZone')
        parser.add_argument('--create-user', type=str, help='Create UpZone approver user')
        parser.add_argument('--upzone-name', type=str, help='UpZone name for the user')
        parser.add_argument('--list-upzones', action='store_true', help='List all UpZones')

    def handle(self, *args, **options):
        if options['create_sample']:
            self.create_sample_upzones()
        
        elif options['create_upzone'] and options['districts']:
            self.create_upzone(options['create_upzone'], options['districts'])
        
        elif options['create_user'] and options['upzone_name']:
            self.create_upzone_user(options['create_user'], options['upzone_name'])
        
        elif options['list_upzones']:
            self.list_upzones()
        
        else:
            self.stdout.write(self.style.ERROR('Please provide valid arguments. Use --help for options.'))

    def create_sample_upzones(self):
        """Create sample UpZones for MP"""
        sample_upzones = [
            {
                'name': 'भोपाल उपजोन',
                'districts': ['Bhopal', 'Raisen', 'Sehore', 'Vidisha']
            },
            {
                'name': 'इंदौर उपजोन', 
                'districts': ['Indore', 'Dewas', 'Ujjain', 'Dhar']
            },
            {
                'name': 'जबलपुर उपजोन',
                'districts': ['Jabalpur', 'Narsinghpur', 'Chhindwara', 'Seoni']
            },
            {
                'name': 'ग्वालियर उपजोन',
                'districts': ['Gwalior', 'Morena', 'Bhind', 'Datia']
            },
            {
                'name': 'सागर उपजोन',
                'districts': ['Sagar', 'Damoh', 'Panna', 'Chhatarpur']
            }
        ]
        
        created_count = 0
        for upzone_data in sample_upzones:
            upzone, created = UpZone.objects.get_or_create(
                name=upzone_data['name'],
                defaults={'districts': upzone_data['districts']}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created UpZone: {upzone.name} with districts: {", ".join(upzone.districts)}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'UpZone already exists: {upzone.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Sample UpZones setup completed. Created {created_count} new UpZones.')
        )

    def create_upzone(self, name, districts):
        """Create a new UpZone"""
        upzone, created = UpZone.objects.get_or_create(
            name=name,
            defaults={'districts': districts}
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created UpZone: {upzone.name} with districts: {", ".join(upzone.districts)}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'UpZone already exists: {upzone.name}')
            )

    def create_upzone_user(self, username, upzone_name):
        """Create UpZone approver user"""
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist. Please create the user first.'))
            return
        
        try:
            upzone = UpZone.objects.get(name=upzone_name)
        except UpZone.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'UpZone {upzone_name} does not exist. Please create the UpZone first.'))
            return
        
        approval_user, created = ApprovalUser.objects.get_or_create(
            user=user,
            defaults={
                'state_code': 'MP',
                'is_upzone_approver': True,
                'upzone': upzone
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created UpZone approver: {user.username} for {upzone.name}')
            )
        else:
            # Update existing user
            approval_user.is_upzone_approver = True
            approval_user.upzone = upzone
            approval_user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated user {user.username} as UpZone approver for {upzone.name}')
            )

    def list_upzones(self):
        """List all UpZones"""
        upzones = UpZone.objects.all().order_by('name')
        if not upzones:
            self.stdout.write(self.style.WARNING('No UpZones found.'))
            return
        
        self.stdout.write(self.style.SUCCESS('UpZones List:'))
        self.stdout.write('-' * 50)
        for upzone in upzones:
            status = "Active" if upzone.is_active else "Inactive"
            districts = ", ".join(upzone.districts) if upzone.districts else "No districts"
            self.stdout.write(f'{upzone.name} ({status}): {districts}')
        
        self.stdout.write('-' * 50)
        self.stdout.write(f'Total UpZones: {upzones.count()}')