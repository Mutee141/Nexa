from django.db import models

# Create your models here.
from django.db import models
from accounts.models import User


class Notification(models.Model):
    TYPE_CHOICES = [
        ('task_assigned',   'Task Assigned'),
        ('task_due',        'Task Due Soon'),
        ('task_completed',  'Task Completed'),
        ('project_update',  'Project Update'),
        ('meeting_reminder','Meeting Reminder'),
        ('meeting_created', 'Meeting Created'),
        ('document_upload', 'Document Uploaded'),
        ('general',         'General'),
    ]

    recipient   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notif_type  = models.CharField(max_length=30, choices=TYPE_CHOICES, default='general')
    title       = models.CharField(max_length=200)
    message     = models.TextField()
    link        = models.CharField(max_length=300, blank=True)
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.email} — {self.title}"

    def get_icon(self):
        icons = {
            'task_assigned':    'fa-list-check',
            'task_due':         'fa-clock',
            'task_completed':   'fa-circle-check',
            'project_update':   'fa-diagram-project',
            'meeting_reminder': 'fa-video',
            'meeting_created':  'fa-calendar-plus',
            'document_upload':  'fa-file-arrow-up',
            'general':          'fa-bell',
        }
        return icons.get(self.notif_type, 'fa-bell')

    def get_color(self):
        colors = {
            'task_assigned':    'indigo',
            'task_due':         'red',
            'task_completed':   'green',
            'project_update':   'violet',
            'meeting_reminder': 'amber',
            'meeting_created':  'blue',
            'document_upload':  'teal',
            'general':          'gray',
        }
        return colors.get(self.notif_type, 'gray')


class NotificationPreference(models.Model):
    user                    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notif_preferences')
    task_assigned           = models.BooleanField(default=True)
    task_due                = models.BooleanField(default=True)
    task_completed          = models.BooleanField(default=True)
    project_update          = models.BooleanField(default=True)
    meeting_reminder        = models.BooleanField(default=True)
    meeting_created         = models.BooleanField(default=True)
    document_upload         = models.BooleanField(default=False)
    email_task_assigned     = models.BooleanField(default=True)
    email_task_due          = models.BooleanField(default=True)
    email_meeting_reminder  = models.BooleanField(default=True)
    email_meeting_created   = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} preferences"