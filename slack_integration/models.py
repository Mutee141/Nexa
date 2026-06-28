from django.db import models
from django.db import models
from accounts.models import User


class SlackSettings(models.Model):
    user           = models.OneToOneField(User, on_delete=models.CASCADE, related_name='slack_settings')
    channel_id     = models.CharField(max_length=50, blank=True)
    channel_name   = models.CharField(max_length=100, blank=True)
    is_enabled     = models.BooleanField(default=False)
    notify_tasks   = models.BooleanField(default=True)
    notify_meetings= models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} Slack settings"