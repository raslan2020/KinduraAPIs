from django.db import models
from django.conf import settings


class FCMToken(models.Model):
    """
    Store FCM tokens for users
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(max_length=20, choices=[
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web'),
    ], default='web')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fcm_tokens'

    def __str__(self):
        return f"{self.user.username} - {self.device_type}"


class NotificationHistory(models.Model):
    """
    Store notification history
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    notification_type = models.CharField(max_length=50, default='medicine_reminder')
    data = models.JSONField(default=dict, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    fcm_response = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'notification_history'
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.user.username} - {self.title} - {self.sent_at}" 