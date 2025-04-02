from django.db import models
from Domains.Onboard.models import Page
from django.contrib.auth import get_user_model

class Upload(models.Model):
    class Meta:
        db_table = 'file_uploads'
    FILE_TYPES = (
        ('txt', 'Text File'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('jpg', 'JPG'),
    )

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=FILE_TYPES)
    path = models.CharField(max_length=255)
    references_page = models.ForeignKey(Page, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()}) - Page: {self.references_page}"
