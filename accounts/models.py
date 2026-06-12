from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    email      = models.EmailField(unique=True)
    avatar     = models.ImageField(upload_to='avatars/', blank=True, null=True)
    job_title  = models.CharField(max_length=100, blank=True)
    phone      = models.CharField(max_length=20, blank=True)
    bio        = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email