from django.db import models
from users.models import User


class Medicine(models.Model):
    """
    Medicine model for managing user medicines
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medicines')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.email}"
    
    class Meta:
        ordering = ['-created_at']
