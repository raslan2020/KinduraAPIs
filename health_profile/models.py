from django.db import models
from users.models import User


class HealthProfile(models.Model):
    """
    Comprehensive health profile for users
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='health_profile')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Health Profile for {self.user.email}"


class LifestyleHabits(models.Model):
    """
    Lifestyle habits information
    """
    health_profile = models.OneToOneField(HealthProfile, on_delete=models.CASCADE, related_name='lifestyle_habits')
    smoking = models.BooleanField(default=False)
    drink_alcohol = models.BooleanField(default=False)
    caffeine_intake = models.PositiveIntegerField(help_text="Cups of tea/coffee/energy drinks per day", default=0)
    
    def __str__(self):
        return f"Lifestyle Habits for {self.health_profile.user.email}"


class PhysicalActivity(models.Model):
    """
    Physical activity information
    """
    health_profile = models.OneToOneField(HealthProfile, on_delete=models.CASCADE, related_name='physical_activity')
    EXERCISE_FREQUENCY_CHOICES = [
        ('never', 'Never'),
        ('1-2', '1-2 times per week'),
        ('3-4', '3-4 times per week'),
        ('5-6', '5-6 times per week'),
        ('daily', 'Daily'),
    ]
    exercise_frequency = models.CharField(max_length=10, choices=EXERCISE_FREQUENCY_CHOICES, default='never')
    exercise_type = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., walking, running, gym, yoga")
    average_duration = models.PositiveIntegerField(help_text="Duration in minutes", blank=True, null=True)
    
    def __str__(self):
        return f"Physical Activity for {self.health_profile.user.email}"


class DietaryHabits(models.Model):
    """
    Dietary habits information
    """
    health_profile = models.OneToOneField(HealthProfile, on_delete=models.CASCADE, related_name='dietary_habits')
    DIET_TYPE_CHOICES = [
        ('vegetarian', 'Vegetarian'),
        ('non_vegetarian', 'Non-vegetarian'),
        ('vegan', 'Vegan'),
        ('other', 'Other'),
    ]
    diet_type = models.CharField(max_length=20, choices=DIET_TYPE_CHOICES, default='non_vegetarian')
    dietary_restrictions = models.TextField(blank=True, null=True, help_text="e.g., allergies, religious, medical")
    daily_water_intake = models.DecimalField(max_digits=4, decimal_places=1, help_text="Liters per day", default=2.0)
    
    def __str__(self):
        return f"Dietary Habits for {self.health_profile.user.email}"


class MedicalHistory(models.Model):
    """
    Medical history information
    """
    health_profile = models.OneToOneField(HealthProfile, on_delete=models.CASCADE, related_name='medical_history')
    taking_medications = models.BooleanField(default=False)
    current_medications = models.TextField(blank=True, null=True, help_text="List of current medications")
    has_allergies = models.BooleanField(default=False)
    allergies = models.TextField(blank=True, null=True, help_text="Specify allergies")
    chronic_conditions = models.TextField(blank=True, null=True, help_text="e.g., diabetes, hypertension")
    
    def __str__(self):
        return f"Medical History for {self.health_profile.user.email}"


class MentalHealth(models.Model):
    """
    Mental health information
    """
    health_profile = models.OneToOneField(HealthProfile, on_delete=models.CASCADE, related_name='mental_health')
    experienced_anxiety_depression = models.BooleanField(default=False)
    seeing_therapist = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Mental Health for {self.health_profile.user.email}"
