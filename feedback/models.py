from django.db import models
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class FeedbackResponse(models.Model):
    RATING_CHOICES = [(i, f'{i} ⭐') for i in range(1, 6)]
    
    # Basic Info
    name = models.CharField(max_length=100, db_index=True)
    contact_number = models.CharField(max_length=15, db_index=True, unique=True)  # Prevent duplicates
    state = models.CharField(max_length=100, db_index=True)
    district = models.CharField(max_length=100, db_index=True)
    
    # Ratings (1-5 stars)
    accommodation_food = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    sessions_activities = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    discipline_management = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    overall_experience = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    cleanliness_facilities = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    staff_helpfulness = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    time_management = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    technical_facilities = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Text Fields
    favorite_session = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    will_join_again = models.BooleanField(default=True)
    inspiration = models.TextField(blank=True)
    
    # Meta
    submission_id = models.CharField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'feedback_response'
        indexes = [
            models.Index(fields=['created_at', 'state']),
            models.Index(fields=['contact_number', 'created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.submission_id:
            import uuid
            self.submission_id = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.district} ({self.overall_experience}/5)"
    
    @property
    def average_rating(self):
        ratings = [
            self.accommodation_food, self.sessions_activities, 
            self.discipline_management, self.overall_experience,
            self.cleanliness_facilities, self.staff_helpfulness,
            self.time_management, self.technical_facilities
        ]
        return round(sum(ratings) / len(ratings), 1)