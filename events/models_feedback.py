from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Feedback(models.Model):
    RATING_CHOICES = [
        (1, '1 - Very Poor'),
        (2, '2 - Poor'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]
    
    FEEDBACK_TYPE_CHOICES = [
        ('event', 'Event Experience'),
        ('website', 'Website Experience'),
        ('registration', 'Registration Process'),
        ('general', 'General Feedback'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES, default='general')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        choices=RATING_CHOICES
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    suggestions = models.TextField(blank=True, help_text="Any suggestions for improvement")
    created_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.rating}/5)"
    
    def get_rating_stars(self):
        return '⭐' * self.rating + '☆' * (5 - self.rating)