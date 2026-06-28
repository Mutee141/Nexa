from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]

    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    created_at = models.DateTimeField(auto_now_add=True)
    has_completed_onboarding = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def is_admin_role(self):
        return self.role == 'admin' or self.is_superuser

    def is_manager_role(self):
        return self.role in ['admin', 'manager'] or self.is_superuser

    def can_manage_billing(self):
        return self.is_admin_role()

    def can_manage_employees(self):
        return self.is_manager_role()

    def can_delete_anything(self):
        return self.is_admin_role()



@receiver(post_save, sender=User)
def create_auth_token(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)