from rest_framework import serializers
from Domains.ManageData.models import Upload

class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upload
        fields = ["name", "path", "type", "uploaded_at"]