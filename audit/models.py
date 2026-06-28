from django.db import models

from django.db import models
from accounts.models import User


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('login',  'Logged in'),
        ('logout', 'Logged out'),
    ]

    user        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action      = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name  = models.CharField(max_length=50)
    object_repr = models.CharField(max_length=255)
    object_id   = models.CharField(max_length=50, blank=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    extra_info  = models.TextField(blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.user} {self.action} {self.model_name} — {self.object_repr}"

    def get_icon(self):
        icons = {'create': 'fa-plus', 'update': 'fa-pen', 'delete': 'fa-trash', 'login': 'fa-right-to-bracket', 'logout': 'fa-right-from-bracket'}
        return icons.get(self.action, 'fa-circle-info')

    def get_color(self):
        colors = {'create': 'green', 'update': 'blue', 'delete': 'red', 'login': 'indigo', 'logout': 'gray'}
        return colors.get(self.action, 'gray')