from rest_framework import serializers
from .models import Upload

class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upload
        fields = ('id', 'path', 'type', 'uploaded_at')
        read_only_fields = ('id', 'uploaded_at')
