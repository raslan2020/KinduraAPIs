from rest_framework import serializers
from .models import Course
from medicines.models import Medicine
from schedules.models import CourseMedicineSchedule


class MedicineCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Medicine model (for nested creation)
    """
    class Meta:
        model = Medicine
        fields = ['name', 'description']


class ScheduleCreateSerializer(serializers.Serializer):
    """
    Serializer for creating schedule data (for nested creation)
    """
    medicine_name = serializers.CharField(max_length=255)
    medicine_description = serializers.CharField(required=False, allow_blank=True)
    time = serializers.TimeField()
    dosage = serializers.CharField(max_length=100)


class CourseWithMedicinesAndSchedulesSerializer(serializers.ModelSerializer):
    """
    Comprehensive course serializer for creating course with medicines and schedules
    """
    medicines_and_schedules = ScheduleCreateSerializer(many=True, required=False)
    
    class Meta:
        model = Course
        fields = [
            'name', 'start_date', 'duration', 'patient_history', 'current_situation',
            'doctor_instructions', 'medicines_and_schedules'
        ]
    
    def validate_start_date(self, value):
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("Start date cannot be in the past")
        return value
    
    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0")
        return value
    
    def create(self, validated_data):
        medicines_and_schedules_data = validated_data.pop('medicines_and_schedules', [])
        
        # Get user from context
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError("User is required to create course")
        
        # Create the course with user
        validated_data['user'] = user
        course = Course.objects.create(**validated_data)
        
        # Create medicines and schedules
        for item in medicines_and_schedules_data:
            # Create or get medicine
            medicine, created = Medicine.objects.get_or_create(
                user=user,
                name=item['medicine_name'],
                defaults={
                    'description': item.get('medicine_description', ''),
                    'is_active': True
                }
            )
            
            # Create schedule
            CourseMedicineSchedule.objects.create(
                course=course,
                medicine=medicine,
                time=item['time'],
                dosage=item['dosage'],
                is_active=True
            )
        
        return course


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for Course model
    """
    class Meta:
        model = Course
        fields = [
            'id', 'name', 'start_date', 'duration', 'patient_history', 'current_situation',
            'doctor_instructions', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_start_date(self, value):
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("Start date cannot be in the past")
        return value
    
    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0")
        return value 