from django.db import models

# Create your models here.
from django.db import models
from accounts.models import User


class Department(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    STATUS_CHOICES = [
        ('active',     'Active'),
        ('inactive',   'Inactive'),
        ('on_leave',   'On Leave'),
        ('terminated', 'Terminated'),
    ]

    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    department      = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    employee_id     = models.CharField(max_length=20, unique=True)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    date_of_joining = models.DateField(blank=True, null=True)
    salary          = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"