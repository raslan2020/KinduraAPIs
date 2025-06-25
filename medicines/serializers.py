from rest_framework import serializers
from .models import Medicine


class MedicineSerializer(serializers.ModelSerializer):
    """
    Serializer for Medicine model
    """
    class Meta:
        model = Medicine
        fields = [
            'id', 'name', 'description', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Medicine name cannot be empty")
        return value.strip() 