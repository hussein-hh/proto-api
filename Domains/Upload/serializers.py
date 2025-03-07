from rest_framework import serializers
from .models import UploadedFile

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ('id', 'path', 'type', 'uploaded_at')
        read_only_fields = ('id', 'uploaded_at')
