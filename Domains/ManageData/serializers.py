from rest_framework import serializers
from .models import CreateUpload

class CreateUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateUpload
        fields = ('id', 'path', 'type', 'uploaded_at')
        read_only_fields = ('id', 'uploaded_at')
