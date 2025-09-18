from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import ApprovalUser, EventRegistration, UpZone

class Command(BaseCommand):
    help = 'Test UpZone user access and filtering'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to test')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"✅ User found: {user.username}")
            
            # Check if user has ApprovalUser record
            try:
                approval_user = ApprovalUser.objects.get(user=user)
                self.stdout.write(f"✅ ApprovalUser found:")
                self.stdout.write(f"   - State Code: {approval_user.state_code}")
                self.stdout.write(f"   - Is District Approver: {approval_user.is_district_approver}")
                self.stdout.write(f"   - Is UpZone Approver: {approval_user.is_upzone_approver}")
                self.stdout.write(f"   - Is State Approver: {approval_user.is_state_approver}")
                self.stdout.write(f"   - UpZone: {approval_user.upzone}")
                self.stdout.write(f"   - Districts: {approval_user.districts}")
                
                if approval_user.upzone:
                    self.stdout.write(f"   - UpZone Districts: {approval_user.upzone.districts}")
                
                # Test queryset filtering
                qs = EventRegistration.objects.all()
                
                if approval_user.state_code == 'MP':
                    if approval_user.is_upzone_approver and approval_user.upzone:
                        upzone_districts = approval_user.upzone.districts or []
                        if upzone_districts:
                            filtered_qs = qs.filter(
                                city__in=upzone_districts,
                                approval_status__in=['district_approved', 'upzone_approved', 'approved']
                            )
                            self.stdout.write(f"✅ Filtered registrations count: {filtered_qs.count()}")
                            
                            # Show some examples
                            for reg in filtered_qs[:5]:
                                self.stdout.write(f"   - {reg.full_name} ({reg.city}) - {reg.approval_status}")
                        else:
                            self.stdout.write("❌ No districts assigned to UpZone")
                    else:
                        self.stdout.write("❌ User is not UpZone approver or no UpZone assigned")
                else:
                    self.stdout.write(f"❌ User state code is not MP: {approval_user.state_code}")
                
            except ApprovalUser.DoesNotExist:
                self.stdout.write("❌ No ApprovalUser record found for this user")
                
        except User.DoesNotExist:
            self.stdout.write(f"❌ User not found: {username}")
        
        # Show all UpZones
        self.stdout.write("\n📋 All UpZones:")
        for upzone in UpZone.objects.all():
            self.stdout.write(f"   - {upzone.name}: {upzone.districts}")
        
        # Show sample registrations
        self.stdout.write(f"\n📋 Sample registrations (total: {EventRegistration.objects.count()}):")
        for reg in EventRegistration.objects.all()[:5]:
            self.stdout.write(f"   - {reg.full_name} ({reg.city}, {reg.state}) - {reg.approval_status}")