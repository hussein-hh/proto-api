from django.db import models
from django.contrib.auth.models import User

class CreateUpload(models.Model):
    class Meta:
        db_table = 'file_uploads'
    FILE_TYPES = (
        ('txt', 'Text File'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('jpg', 'JPG'),
    )

    path = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=FILE_TYPES)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.type} file uploaded by {self.uploaded_by.username}"
