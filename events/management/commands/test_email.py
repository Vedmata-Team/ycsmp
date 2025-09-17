from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from events.models import EventRegistration
from events.email_utils import send_registration_approval_email

class Command(BaseCommand):
    help = 'Test email functionality'

    def add_arguments(self, parser):
        parser.add_argument('--registration-id', type=int, help='Registration ID to test email')
        parser.add_argument('--test-basic', action='store_true', help='Test basic email sending')

    def handle(self, *args, **options):
        if options['test_basic']:
            self.stdout.write('Testing basic email sending...')
            try:
                send_mail(
                    subject='Test Email from YCSMP',
                    message='This is a test email to verify email configuration.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['youthcell@awgp.org'],  # Send to self for testing
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS('Basic email test successful!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Basic email test failed: {e}'))
                import traceback
                self.stdout.write(traceback.format_exc())

        if options['registration_id']:
            try:
                registration = EventRegistration.objects.get(pk=options['registration_id'])
                self.stdout.write(f'Testing email for registration: {registration.full_name} ({registration.email})')
                
                if send_registration_approval_email(registration):
                    self.stdout.write(self.style.SUCCESS('Registration email sent successfully!'))
                else:
                    self.stdout.write(self.style.ERROR('Registration email sending failed!'))
            except EventRegistration.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Registration with ID {options["registration_id"]} not found'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {e}'))
                import traceback
                self.stdout.write(traceback.format_exc())