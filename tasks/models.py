from django.db import models

# Create your models here.
from django.db import models
from accounts.models import User


class Project(models.Model):
    STATUS_CHOICES = [
        ('planning',    'Planning'),
        ('active',      'Active'),
        ('on_hold',     'On Hold'),
        ('completed',   'Completed'),
        ('cancelled',   'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('low',      'Low'),
        ('medium',   'Medium'),
        ('high',     'High'),
        ('critical', 'Critical'),
    ]

    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    priority    = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    owner       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    members     = models.ManyToManyField(User, related_name='projects', blank=True)
    start_date  = models.DateField(blank=True, null=True)
    end_date    = models.DateField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Task(models.Model):
    STATUS_CHOICES = [
        ('todo',        'To Do'),
        ('in_progress', 'In Progress'),
        ('review',      'In Review'),
        ('done',        'Done'),
    ]
    PRIORITY_CHOICES = [
        ('low',      'Low'),
        ('medium',   'Medium'),
        ('high',     'High'),
        ('critical', 'Critical'),
    ]

    title       = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority    = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    project     = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    due_date    = models.DateField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']