from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
import csv
import os
from django.conf import settings

from events.utils import compress_regular_image

class ApprovalUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    state_code = models.CharField(max_length=10, verbose_name="राज्य कोड")
    districts = models.JSONField(default=list, blank=True, verbose_name="जिले")  # For MP users
    is_state_approver = models.BooleanField(default=False, verbose_name="राज्य अप्रूवर")
    is_district_approver = models.BooleanField(default=False, verbose_name="जिला अप्रूवर")
    
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
        if self.is_district_approver and self.districts:
            return f"{len(self.districts)} जिले"
        elif self.is_state_approver:
            return f"1 राज्य ({self.state_code})"
        return "कोई असाइनमेंट नहीं"

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

class EventRegistration(models.Model):
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
    registration_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    # Personal Information
    full_name = models.CharField(max_length=100, verbose_name="नाम")
    phone = models.CharField(max_length=15, verbose_name="मोबाइल नं.")
    email = models.EmailField(verbose_name="ईमेल")
    date_of_birth = models.DateField(verbose_name="जन्म तिथि")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="लिंग")
    models.
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
    
    # Education & Skills
    education = models.CharField(max_length=50, choices=EDUCATION_CHOICES, verbose_name="शैक्षणिक योग्यता")
    occupation = models.CharField(max_length=100, verbose_name="व्यवसाय", blank=True, null=True)
    special_skills = models.JSONField(default=list, blank=True, verbose_name="विशेष कौशल")
    special_skills_other = models.TextField(blank=True, verbose_name="अन्य विशेष कौशल")
    
    # Address
    village_taluka = models.CharField(max_length=100, verbose_name="गांव/तालुका")
    country = models.CharField(max_length=64, default='India', blank=True, verbose_name="देश")
    state = models.CharField(max_length=64, verbose_name="राज्य")
    city = models.CharField(max_length=64, verbose_name="जनपद/जिला")
    
    # Other Details
    arrival_date = models.DateField(verbose_name="आगमन तिथि")
    departure_date = models.DateField(verbose_name="प्रस्थान तिथि")
    
    # Volunteering
    interested_in_volunteering = models.BooleanField(default=False, verbose_name="क्या आप किसी विशेष टीम/सेवा में योगदान देना चाहते हैं?")
    volunteering_details = models.TextField(blank=True, verbose_name="आप कैसे योगदान देना चाहते हैं?")
    
    # Campaigns (stored as JSON)
    selected_campaigns = models.JSONField(default=list, verbose_name="चयनित अभियान")
    
    # Approval System
    approval_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'प्रतीक्षारत'),
            ('level1_approved', 'स्तर 1 अप्रूव'),
            ('approved', 'अप्रूव'),
            ('rejected', 'अस्वीकृत')
        ],
        default='pending',
        verbose_name="अप्रूवल स्थिति"
    )
    level1_approver = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='level1_approvals', verbose_name="स्तर 1 अप्रूवर")
    level1_approved_at = models.DateTimeField(null=True, blank=True, verbose_name="स्तर 1 अप्रूवल समय")
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
        if approval_user.state_code == 'MP' and approval_user.is_district_approver:
            # For MP, check district assignment
            return self.city in approval_user.districts if approval_user.districts else False
        elif approval_user.is_state_approver:
            # For other states, check state assignment
            return self.state_code == approval_user.state_code
        return False

    class Meta:
        verbose_name = "पंजीकरण"
        verbose_name_plural = "पंजीकरण"
        ordering = ['-registration_date']

    def __str__(self):
        return f"{self.full_name} - {self.event.title}"

    def save(self, *args, **kwargs):
        is_newly_approved = False
        if self.pk:
            old_instance = EventRegistration.objects.get(pk=self.pk)
            is_newly_approved = (old_instance.approval_status != 'approved' and self.approval_status == 'approved')
            
            if is_newly_approved and not self.registration_number:
                self.registration_number = self.generate_registration_number()
                self.is_confirmed = True
        
        super().save(*args, **kwargs)
        
        if is_newly_approved and not self.email_sent:
            from .email_utils import send_registration_approval_email
            if send_registration_approval_email(self):
                self.email_sent = True
                super().save(update_fields=['email_sent'])
    
    def get_approver_for_registration(self):
        """Get appropriate approver based on state"""
        state_code = self.state_code
        if state_code == 'MP':
            # For MP, find district-wise approver
            return ApprovalUser.objects.filter(
                state_code='MP',
                is_district_approver=True,
                districts__contains=[self.city]
            ).first()
        else:
            # For other states, find state-wise approver
            return ApprovalUser.objects.filter(
                state_code=state_code,
                is_state_approver=True
            ).first()
    
    def generate_registration_number(self):
        """Generate registration number: YCS-StateCode-CityPrefix-SerialNumber"""
        from django.db import transaction
        
        state_code = self.state_code or 'XX'
        city_prefix = self.city[:3].upper() if self.city else 'XXX'
        
        with transaction.atomic():
            # Get the highest existing serial number for this city
            existing_regs = EventRegistration.objects.filter(
                city=self.city,
                registration_number__isnull=False
            ).exclude(pk=self.pk or 0)
            
            max_serial = 0
            prefix = f"YCS-{state_code}-{city_prefix}-"
            
            for reg in existing_regs:
                if reg.registration_number and reg.registration_number.startswith(prefix):
                    try:
                        serial_part = reg.registration_number.split('-')[-1]
                        serial_num = int(serial_part)
                        max_serial = max(max_serial, serial_num)
                    except (ValueError, IndexError):
                        continue
            
            new_serial = max_serial + 1
            return f"YCS-{state_code}-{city_prefix}-{new_serial:04d}"

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

class ApprovalUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="यूजर")
    state_code = models.CharField(max_length=10, verbose_name="राज्य कोड")
    is_state_approver = models.BooleanField(default=False, verbose_name="राज्य अप्रूवर")
    is_district_approver = models.BooleanField(default=False, verbose_name="जिला अप्रूवर")
    districts = models.JSONField(default=list, blank=True, verbose_name="जिले")
    
    class Meta:
        verbose_name = "अप्रूवल यूजर"
        verbose_name_plural = "अप्रूवल यूजर"
    
    def __str__(self):
        return f"{self.user.username} - {self.state_code}"
    
    def get_assignment_display(self):
        if self.state_code == 'MP' and self.is_district_approver:
            return f"MP जिले: {', '.join(self.districts) if self.districts else 'कोई नहीं'}"
        elif self.is_state_approver:
            return f"राज्य: {self.state_code}"
        return "कोई असाइनमेंट नहीं"