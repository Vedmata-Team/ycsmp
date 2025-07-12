from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import ApprovalUser


class Command(BaseCommand):
    help = 'Setup approval users for registration filtering'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username to setup as approval user')
        parser.add_argument('--state-code', type=str, help='State code (e.g., UP, MP, RJ)')
        parser.add_argument('--districts', nargs='*', help='Districts for MP state (space separated)')
        parser.add_argument('--list-users', action='store_true', help='List all approval users')

    def handle(self, *args, **options):
        if options['list_users']:
            self.list_approval_users()
            return

        username = options.get('username')
        state_code = options.get('state_code')
        districts = options.get('districts', [])

        if not username or not state_code:
            self.stdout.write(
                self.style.ERROR('Both --username and --state-code are required')
            )
            return

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist')
            )
            return

        # Create or update ApprovalUser
        approval_user, created = ApprovalUser.objects.get_or_create(
            user=user,
            defaults={
                'state_code': state_code,
                'is_state_approver': state_code != 'MP',
                'is_district_approver': state_code == 'MP',
                'districts': districts if state_code == 'MP' else []
            }
        )

        if not created:
            approval_user.state_code = state_code
            approval_user.is_state_approver = state_code != 'MP'
            approval_user.is_district_approver = state_code == 'MP'
            approval_user.districts = districts if state_code == 'MP' else []
            approval_user.save()

        action = 'Created' if created else 'Updated'
        self.stdout.write(
            self.style.SUCCESS(
                f'{action} approval user for {username} - {state_code}'
            )
        )

        if state_code == 'MP' and districts:
            self.stdout.write(f'  Districts: {", ".join(districts)}')

    def list_approval_users(self):
        approval_users = ApprovalUser.objects.all()
        if not approval_users:
            self.stdout.write('No approval users found')
            return

        self.stdout.write('\nApproval Users:')
        self.stdout.write('-' * 50)
        for au in approval_users:
            self.stdout.write(f'User: {au.user.username}')
            self.stdout.write(f'State: {au.state_code}')
            if au.state_code == 'MP' and au.districts:
                self.stdout.write(f'Districts: {", ".join(au.districts)}')
            self.stdout.write(f'Assignment: {au.get_assignment_display()}')
            self.stdout.write('-' * 30)