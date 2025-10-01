from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
import csv
import os
from django.conf import settings

from events.utils import compress_regular_image
from .models_location import StateDistrict

# Location Models
class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    
    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name}, {self.state.name}"

class UpZone(models.Model):
    name = models.CharField(max_length=100, verbose_name="उपजोन नाम")
    districts = models.JSONField(default=list, verbose_name="जिले")
    is_active = models.BooleanField(default=True, verbose_name="सक्रिय")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "उपजोन"
        verbose_name_plural = "उपजोन"
    
    def __str__(self):
        return self.name
    
    def get_districts_display(self):
        return ', '.join(self.districts) if self.districts else 'कोई जिला नहीं'

class ApprovalUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    state_code = models.CharField(max_length=10, verbose_name="राज्य कोड")
    districts = models.JSONField(default=list, blank=True, verbose_name="जिले")  # For MP users
    upzone = models.ForeignKey(UpZone, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="उपजोन")
    is_super_approver = models.BooleanField(default=False, verbose_name="सुपर अप्रूवर (सभी स्तर)")
    is_state_approver = models.BooleanField(default=False, verbose_name="राज्य अप्रूवर")
    is_district_approver = models.BooleanField(default=False, verbose_name="जिला अप्रूवर")
    is_upzone_approver = models.BooleanField(default=False, verbose_name="उपजोन अप्रूवर")
    allowed_registration_types = models.JSONField(default=list, blank=True, verbose_name="अनुमतित पंजीकरण प्रकार")
    
    class Meta:
        verbose_name = "अप्रूवल यूजर"
        verbose_name_plural = "अप्रूवल यूजर"
    
    def __str__(self):
        return f"{self.user.username} - {self.state_code}"
    
    def get_assigned_count(self):
        """Get count of assigned districts or states"""
        if self.is_district_approver and self.districts:
            return len(self.districts)
        elif self.is_state_approver:
            return 1
        return 0
    
    def get_assignment_display(self):
        """Display assignment details"""
        assignment = ""
        if self.is_super_approver:
            assignment = "सभी देश (सुपर अप्रूवर)"
        elif self.is_district_approver and self.districts:
            assignment = f"{len(self.districts)} जिले"
        elif self.is_upzone_approver and self.upzone:
            assignment = f"उपजोन: {self.upzone.name}"
        elif self.is_state_approver:
            assignment = f"1 राज्य ({self.state_code})"
        else:
            assignment = "कोई असाइनमेंट नहीं"
        
        # Add registration types if specified
        if self.allowed_registration_types:
            reg_types = [dict(EventRegistration.REGISTRATION_TYPE_CHOICES).get(rt, rt) for rt in self.allowed_registration_types]
            assignment += f" | प्रकार: {', '.join(reg_types)}"
        
        return assignment

class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="कार्यक्रम नाम")
    slug = models.SlugField(unique=True, blank=True)
    description = RichTextUploadingField(verbose_name="विवरण")
    category = models.CharField(max_length=100, verbose_name="श्रेणी")

    district = models.CharField(max_length=100, verbose_name="जिला", null=True, blank=True)

    venue = models.CharField(max_length=200, verbose_name="स्थान")
    event_date = models.DateTimeField(verbose_name="कार्यक्रम तिथि")
    registration_deadline = models.DateTimeField(verbose_name="पंजीकरण अंतिम तिथि")
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="पंजीकरण शुल्क")
    max_participants = models.PositiveIntegerField(default=100, verbose_name="अधिकतम प्रतिभागी")
    is_published = models.BooleanField(default=True, verbose_name="प्रकाशित")
    is_featured = models.BooleanField(default=False, verbose_name="मुख्य कार्यक्रम")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "कार्यक्रम"
        verbose_name_plural = "कार्यक्रम"
        ordering = ['event_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('events:detail', kwargs={'pk': self.pk})

    @property
    def registered_count(self):
        return self.registrations.filter(approval_status='approved').count()

    @property
    def available_spots(self):
        return self.max_participants - self.registered_count

    @property
    def registration_percentage(self):
        if self.max_participants > 0:
            return round((self.registered_count / self.max_participants) * 100, 1)
        return 0

class ResponsibilityOption(models.Model):
    name = models.CharField(max_length=100, verbose_name="जिम्मेदारी नाम")
    order = models.PositiveIntegerField(default=0, verbose_name="क्रम")
    is_active = models.BooleanField(default=True, verbose_name="सक्रिय")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "जिम्मेदारी विकल्प"
        verbose_name_plural = "जिम्मेदारी विकल्प"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class VibhagOption(models.Model):
    name = models.CharField(max_length=100, verbose_name="विभाग नाम")
    order = models.PositiveIntegerField(default=0, verbose_name="क्रम")
    is_active = models.BooleanField(default=True, verbose_name="सक्रिय")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "विभाग विकल्प"
        verbose_name_plural = "विभाग विकल्प"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class EventRegistration(models.Model):
    REGISTRATION_TYPE_CHOICES = [
        ('participant', 'प्रतिभागी'),
        ('volunteer', 'समयदानी कार्यकर्ता'),
        ('organization_representative', 'संगठन प्रतिनिधि'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'पुरुष'),
        ('F', 'महिला'),
        ('O', 'अन्य'),
    ]
    
    CAMPAIGN_CHOICES = [
        ('youth_connect', 'युवा जोड़ो अभियान'),
        ('water_cleanliness', 'जल शुद्धि, स्वच्छता'),
        ('tree_ganga', 'वृक्ष गंगा अभियान'),
        ('ideal_village', 'आदर्श ग्राम व्यसनमुक्ति'),
        ('sadhana', 'साधना'),
        ('health', 'स्वास्थ्य'),
        ('literature', 'साहित्य विस्तार'),
        ('self_reliance', 'स्वावलंबन'),
        ('newlywed_camp', 'नवदंपत्ति शिविर'),
        ('pregnancy_sanskar', 'गर्भ संस्कार'),
        ('mother_sanskar', 'माँ की संस्कारशाला'),
        ('child_sanskar', 'बाल संस्कारशाला'),
        ('girl_teen_skill', 'कन्या किशोर कौशल'),
    ]
    
    EDUCATION_CHOICES = [
        ('high_school', 'हाई स्कूल (10वीं)'),
        ('intermediate', 'इंटरमीडिएट (12वीं)'),
        ('graduation', 'स्नातक (Graduation – BA/BSc/BCom)'),
        ('graduation_tech', 'स्नातक तकनीकी (B.Tech/BCA/BBA)'),
        ('post_graduation', 'परास्नातक (Post Graduation – MA/MSc/MCom)'),
        ('post_graduation_tech', 'परास्नातक तकनीकी (M.Tech/MBA/MCA)'),
        ('iti_diploma', 'आईटीआई / डिप्लोमा'),
        ('sanskrit', 'संस्कृत शिक्षा (शास्त्री / आचार्य)'),
    ]
    
    SPECIAL_SKILLS_CHOICES = [
        ('music', 'संगीत'),
        ('dance', 'नृत्य'),
        ('art', 'कला'),
        ('writing', 'लेखन'),
        ('speaking', 'भाषण'),
        ('teaching', 'शिक्षण'),
        ('cooking', 'रसोई संचालन'),
        ('sports', 'खेल'),
        ('technology', 'तकनीकी'),
        ('photography', 'फोटोग्राफी'),
        ('other', 'अन्य'),
    ]

    event = models.ForeignKey(Event, related_name='registrations', on_delete=models.CASCADE)
    registration_type = models.CharField(max_length=30, choices=REGISTRATION_TYPE_CHOICES, default='participant', verbose_name="पंजीकरण प्रकार")
    registration_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    # Personal Information
    full_name = models.CharField(max_length=100, verbose_name="नाम")
    phone = models.CharField(max_length=15, verbose_name="मोबाइल नं.")
    email = models.EmailField(verbose_name="ईमेल")
    date_of_birth = models.DateField(verbose_name="जन्म तिथि")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="लिंग")
    
    # Transport Information
    TRANSPORT_CHOICES = [
        ('car', 'कार'),
        ('bike', 'बाइक'),
        ('bus', 'बस'),
        ('train', 'ट्रेन'),
        ('auto', 'ऑटो/टैक्सी'),
        ('walking', 'पैदल'),
        ('other', 'अन्य'),
    ]
    
    transport_mode = models.CharField(max_length=20, choices=TRANSPORT_CHOICES, verbose_name="आप किस माध्यम से कार्यक्रम स्थल तक पहुंचेंगे?")
    vehicle_number = models.CharField(max_length=20, blank=True, verbose_name="वाहन नंबर")
    
    # Previous Experience
    previous_shivir = models.BooleanField(default=False, verbose_name="क्या आप शांतिकुंज या अन्य शाखाओं में पहले कोई शिविर कर चुके हैं?")
    gayatri_diksha = models.BooleanField(null=True, blank=True, verbose_name="क्या आपने गायत्री दीक्षा ली है?")
    
    # Education & Skills
    education = models.CharField(max_length=50, choices=EDUCATION_CHOICES, verbose_name="शैक्षणिक योग्यता")
    occupation = models.CharField(max_length=100, verbose_name="व्यवसाय", blank=True, null=True)
    special_skills = models.JSONField(default=list, blank=True, verbose_name="विशेष कौशल")
    special_skills_other = models.TextField(blank=True, verbose_name="अन्य विशेष कौशल")
    
    # Address
    village_taluka = models.CharField(max_length=100, verbose_name="गांव/तालुका")
    country = models.CharField(max_length=64, default='India', blank=True, verbose_name="देश")
    state = models.CharField(max_length=64, verbose_name="राज्य")
    city = models.CharField(max_length=64, verbose_name="जिला")
    
    # Other Details
    ARRIVAL_DATE_CHOICES = [
        ('2025-10-25', '25 अक्टूबर 2025'),
        ('2025-10-26', '26 अक्टूबर 2025'),
    ]
    arrival_date = models.CharField(max_length=10, choices=ARRIVAL_DATE_CHOICES, verbose_name="आगमन तिथि")
    
    # Volunteering
    interested_in_volunteering = models.BooleanField(default=False, verbose_name="क्या आप किसी विशेष टीम/सेवा में योगदान देना चाहते हैं?")
    volunteering_details = models.TextField(blank=True, verbose_name="आप कैसे योगदान देना चाहते हैं?")
    
    # Volunteer Vibhag (Department) - Multiple selection for volunteers
    selected_vibhags = models.JSONField(default=list, blank=True, verbose_name="चयनित विभाग")
    
    # Campaigns (stored as JSON)
    selected_campaigns = models.JSONField(default=list, verbose_name="चयनित अभियान")
    
    # Organization Representative specific fields
    responsibility = models.ForeignKey(ResponsibilityOption, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="जिम्मेदारी")
    
    # Volunteer specific fields
    volunteer_start_date = models.DateField(null=True, blank=True, verbose_name="समयदान प्रारंभ तिथि")
    volunteer_end_date = models.DateField(null=True, blank=True, verbose_name="समयदान समाप्ति तिथि")
    
    # Document uploads (only for participant registration) - stored as URLs
    aadhar_upload_type = models.CharField(
        max_length=20,
        choices=[('full', 'पूरा आधार'), ('separate', 'अलग-अलग (आगे-पीछे)')],
        null=True, blank=True,
        verbose_name="आधार अपलोड प्रकार"
    )
    aadhar_full = models.URLField(null=True, blank=True, verbose_name="पूरा आधार")
    aadhar_front = models.URLField(null=True, blank=True, verbose_name="आधार आगे")
    aadhar_back = models.URLField(null=True, blank=True, verbose_name="आधार पीछे")
    passport_photo = models.URLField(null=True, blank=True, verbose_name="पासपोर्ट फोटो")
    
    # 3-Level Approval System: District → UpZone → State
    approval_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'प्रतीक्षारत'),
            ('district_approved', 'जिला अप्रूव'),
            ('upzone_approved', 'उपजोन अप्रूव'),
            ('approved', 'अप्रूव'),
            ('rejected', 'अस्वीकृत')
        ],
        default='pending',
        verbose_name="अप्रूवल स्थिति"
    )
    district_approver = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='district_approvals', verbose_name="जिला अप्रूवर")
    district_approved_at = models.DateTimeField(null=True, blank=True, verbose_name="जिला अप्रूवल समय")
    upzone_approver = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='upzone_approvals', verbose_name="उपजोन अप्रूवर")
    upzone_approved_at = models.DateTimeField(null=True, blank=True, verbose_name="उपजोन अप्रूवल समय")
    final_approver = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='final_approvals', verbose_name="अंतिम अप्रूवर")
    final_approved_at = models.DateTimeField(null=True, blank=True, verbose_name="अंतिम अप्रूवल समय")
    rejection_reason = models.TextField(blank=True, verbose_name="अस्वीकृति कारण")
    
    is_confirmed = models.BooleanField(default=False, verbose_name="पुष्ट")
    registration_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.BooleanField(default=False, verbose_name="भुगतान स्थिति")
    email_sent = models.BooleanField(default=False, verbose_name="ईमेल भेजा गया")
    
    @property
    def state_code(self):
        """Get state code from CSV"""
        try:
            csv_path = os.path.join(settings.STATICFILES_DIRS[0], 'csv', 'states.csv')
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['name'].lower().strip() == self.state.lower().strip():
                        return row['state_code']
        except:
            pass
        return None
    
    def matches_approval_user(self, approval_user):
        """Check if this registration matches the approval user's assignment"""
        # First check registration type permission
        if approval_user.allowed_registration_types and self.registration_type not in approval_user.allowed_registration_types:
            return False
        
        if approval_user.state_code == 'MP':
            if approval_user.is_district_approver:
                # District level - check district assignment
                return self.city in approval_user.districts if approval_user.districts else False
            elif approval_user.is_upzone_approver and approval_user.upzone:
                # UpZone level - check if registration's district is in upzone
                return self.city in approval_user.upzone.districts if approval_user.upzone.districts else False
            elif approval_user.is_state_approver:
                # State level - check state
                return True
        elif approval_user.is_state_approver:
            # For other states, check state assignment
            return self.state_code == approval_user.state_code
        return False
    
    def get_upzone_for_district(self):
        """Get UpZone for this registration's district with caching"""
        if self.state_code == 'MP':
            # Try cache first
            from django.core.cache import cache
            cache_key = f"upzone_{self.city.replace(' ', '_')}_MP"
            upzone = cache.get(cache_key)
            
            if upzone is None:
                upzone = UpZone.objects.filter(
                    districts__contains=[self.city], 
                    is_active=True
                ).exclude(name='MP Central Zone').first()
                # Cache for 1 hour
                cache.set(cache_key, upzone, 3600)
            
            return upzone
        return None

    class Meta:
        verbose_name = "पंजीकरण"
        verbose_name_plural = "पंजीकरण"
        ordering = ['-registration_date']
        permissions = [
            ('view_all_eventregistration', 'Can view all registrations'),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.event.title}"
    
    def get_profile_url(self):
        """Generate unique profile URL with phone and name"""
        # Clean name: replace spaces with underscores, remove special chars
        clean_name = self.full_name.replace(' ', '_').replace('-', '_')
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
        
        profile_id = f"{self.phone}_{clean_name}"
        return f"/profile/{profile_id}/"

    def save(self, *args, **kwargs):
        # Validate vibhag data integrity
        if self.selected_vibhags and isinstance(self.selected_vibhags, list):
            # Ensure all vibhag IDs are valid
            try:
                vibhag_ids = [int(vid) for vid in self.selected_vibhags if str(vid).isdigit()]
                valid_vibhags = VibhagOption.objects.filter(id__in=vibhag_ids, is_active=True)
                if len(vibhag_ids) != valid_vibhags.count():
                    # Log invalid vibhag IDs but don't fail
                    invalid_ids = set(vibhag_ids) - set(valid_vibhags.values_list('id', flat=True))
                    print(f"Warning: Invalid vibhag IDs found: {invalid_ids}")
            except Exception as e:
                print(f"Warning: Vibhag validation error: {e}")
        
        # Validate campaign data integrity
        if self.selected_campaigns and isinstance(self.selected_campaigns, list):
            valid_campaigns = [choice[0] for choice in self.CAMPAIGN_CHOICES]
            invalid_campaigns = [c for c in self.selected_campaigns if c not in valid_campaigns]
            if invalid_campaigns:
                print(f"Warning: Invalid campaign codes found: {invalid_campaigns}")
        
        is_newly_approved = False
        if self.pk:
            old_instance = EventRegistration.objects.get(pk=self.pk)
            is_newly_approved = (old_instance.approval_status != 'approved' and self.approval_status == 'approved')
            
            if is_newly_approved and not self.registration_number:
                self.registration_number = self.generate_registration_number()
                self.is_confirmed = True
        
        super().save(*args, **kwargs)
        
        # Send email when registration is approved
        if is_newly_approved and not self.email_sent:
            from .email_utils import send_registration_approval_email
            try:
                if send_registration_approval_email(self):
                    self.email_sent = True
                    # Use update to avoid recursion
                    EventRegistration.objects.filter(pk=self.pk).update(email_sent=True)
                    print(f"Approval email sent to {self.email}")
                else:
                    print(f"Failed to send approval email to {self.email}")
            except Exception as e:
                print(f"Error sending approval email to {self.email}: {str(e)}")

    
    def get_approver_for_registration(self, level='district'):
        """Get appropriate approver based on state and level"""
        state_code = self.state_code
        if state_code == 'MP':
            if level == 'district':
                # For MP, find district-wise approver
                return ApprovalUser.objects.filter(
                    state_code='MP',
                    is_district_approver=True,
                    districts__contains=[self.city]
                ).first()
            elif level == 'upzone':
                # Find upzone approver for this district
                upzone = self.get_upzone_for_district()
                if upzone:
                    return ApprovalUser.objects.filter(
                        state_code='MP',
                        is_upzone_approver=True,
                        upzone=upzone
                    ).first()
            elif level == 'state':
                # Find state approver
                return ApprovalUser.objects.filter(
                    state_code='MP',
                    is_state_approver=True
                ).first()
        else:
            # For other states, find state-wise approver
            return ApprovalUser.objects.filter(
                state_code=state_code,
                is_state_approver=True
            ).first()
        return None
    
    def get_campaign_names(self):
        """Get readable campaign names for export"""
        if self.selected_campaigns:
            campaign_dict = dict(self.CAMPAIGN_CHOICES)
            campaign_names = [campaign_dict.get(code, code) for code in self.selected_campaigns]
            return ', '.join(campaign_names)
        return ''
    
    def get_vibhag_names(self):
        """Get readable vibhag names for export"""
        if self.selected_vibhags:
            try:
                vibhag_ids = [int(vid) for vid in self.selected_vibhags if str(vid).isdigit()]
                vibhags = VibhagOption.objects.filter(id__in=vibhag_ids)
                return ', '.join([v.name for v in vibhags])
            except:
                return str(self.selected_vibhags)
        return ''
    
    def generate_registration_number(self):
        """Generate registration number: YCS/YCSV-StateCode-CityPrefix-SerialNumber"""
        from django.db import transaction
        
        state_code = self.state_code or 'XX'
        city_prefix = self.city[:3].upper() if self.city else 'XXX'
        
        # Different prefix for each registration type
        if self.registration_type == 'volunteer':
            base_prefix = 'YCSV'
        elif self.registration_type == 'organization_representative':
            base_prefix = 'YCSO'
        else:
            base_prefix = 'YCS'
        
        with transaction.atomic():
            # Get the highest existing serial number for this city and registration type
            existing_regs = EventRegistration.objects.filter(
                city=self.city,
                registration_type=self.registration_type,
                registration_number__isnull=False
            ).exclude(pk=self.pk or 0)
            
            max_serial = 0
            prefix = f"{base_prefix}-{state_code}-{city_prefix}-"
            
            for reg in existing_regs:
                if reg.registration_number and reg.registration_number.startswith(prefix):
                    try:
                        serial_part = reg.registration_number.split('-')[-1]
                        serial_num = int(serial_part)
                        max_serial = max(max_serial, serial_num)
                    except (ValueError, IndexError):
                        continue
            
            new_serial = max_serial + 1
            return f"{base_prefix}-{state_code}-{city_prefix}-{new_serial:04d}"

class EventImage(models.Model):
    event = models.ForeignKey(Event, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='event_images/', verbose_name="छवि")
    caption = models.CharField(max_length=200, blank=True, verbose_name="कैप्शन")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "कार्यक्रम छवि"
        verbose_name_plural = "कार्यक्रम छवियां"

    def save(self, *args, **kwargs):
        if self.image:
            self.image = compress_regular_image(self.image)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.event.title} - Image"

