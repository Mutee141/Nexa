from django.db import models

# Create your models here.
import uuid
from django.db import models
from accounts.models import User


class Invite(models.Model):
    ROLE_CHOICES = [
        ('admin',    'Admin'),
        ('manager',  'Manager'),
        ('employee', 'Employee'),
    ]

    email      = models.EmailField()
    token      = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invites')
    is_used    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invite to {self.email}"

    def is_expired(self):
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(days=7)