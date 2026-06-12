from django.db import models

# Create your models here.
from django.db import models
from accounts.models import User


class Meeting(models.Model):
    STATUS_CHOICES = [
        ('scheduled',  'Scheduled'),
        ('completed',  'Completed'),
        ('cancelled',  'Cancelled'),
    ]

    title        = models.CharField(max_length=200)
    description  = models.TextField(blank=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    organizer    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_meetings')
    attendees    = models.ManyToManyField(User, related_name='meetings', blank=True)
    start_time   = models.DateTimeField()
    end_time     = models.DateTimeField()
    location     = models.CharField(max_length=200, blank=True)
    meeting_link = models.URLField(blank=True)
    notes        = models.TextField(blank=True)
    ai_summary   = models.TextField(blank=True)   # AI will fill this
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-start_time']