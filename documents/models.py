from django.db import models

# Create your models here.
from django.db import models
from accounts.models import User


class Document(models.Model):
    CATEGORY_CHOICES = [
        ('general',   'General'),
        ('hr',        'HR'),
        ('finance',   'Finance'),
        ('legal',     'Legal'),
        ('technical', 'Technical'),
        ('policy',    'Policy'),
    ]

    title       = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    file        = models.FileField(upload_to='documents/%Y/%m/')
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    ai_summary  = models.TextField(blank=True)   # AI will fill this
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']