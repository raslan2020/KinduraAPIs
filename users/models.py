from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """
    Custom User model for the medical app
    """
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    language = models.CharField(default='en')
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    AGENT_CONSERVATION_CHOICES = [
        ('S', 'Short'),
        ('M', 'Medium'),
        ('D', 'Detailed'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='S' ,blank=True, null=True)
    agent_conservation_choice = models.CharField(max_length=1, choices=AGENT_CONSERVATION_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    terms_and_conditions = models.BooleanField(default=False)
    
    # Override username field to use email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def clean(self):
        super().clean()
        if self.age and self.age > 150:
            raise ValidationError('Age cannot be greater than 150')
    
    def __str__(self):
        return self.email


class UserToken(models.Model):
    """
    Simple token model for user authentication
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Token for {self.user.email}"
    
    class Meta:
        db_table = 'user_tokens'


class UserJSON(models.Model):
    """
    Model to store uploaded JSON data for each user
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='json_uploads')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    summarize_patient_report = models.CharField(null=True, blank=True) 
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"JSON upload by {self.user.email} at {self.uploaded_at} (Status: {self.status})"
