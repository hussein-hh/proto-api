from rest_framework import serializers
from .models import Business, RoleModel

class BusinessSerializer(serializers.ModelSerializer):
    role_model = serializers.PrimaryKeyRelatedField(
        queryset=RoleModel.objects.all(), 
        required=False, 
        allow_null=True
    )

    class Meta:
        model = Business
        fields = ['id', 'user', 'name', 'category', 'role_model']
        read_only_fields = ['id', 'user']