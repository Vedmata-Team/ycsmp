from django.db import models

class SiteWarning(models.Model):
    title = models.CharField(max_length=200, verbose_name="चेतावनी शीर्षक")
    message = models.TextField(verbose_name="चेतावनी संदेश")
    is_active = models.BooleanField(default=True, verbose_name="सक्रिय")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "साइट चेतावनी"
        verbose_name_plural = "साइट चेतावनी"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title