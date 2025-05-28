from django.db import models
from Domains.Onboard.models import Page
from django.contrib.auth import get_user_model

class Upload(models.Model):
    class Meta:
        db_table = 'file_uploads'

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10)
    path = models.CharField(max_length=255)
    references_page = models.ForeignKey(Page, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    uba_report = models.CharField(max_length=255, null=True)
    web_metrics_report = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.type}) - Page: {self.references_page}"
