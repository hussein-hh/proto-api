from rest_framework import serializers
from .models import Business

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['id', 'user', 'name', 'category', 'url', 'goal']
        read_only_fields = ['id', 'user']
