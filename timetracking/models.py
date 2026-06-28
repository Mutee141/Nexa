from django.db import models

# Create your models here.
from django.db import models
from accounts.models import User
from tasks.models import Task, Project


class TimeEntry(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_entries')
    task        = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_entries', null=True, blank=True)
    project     = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='time_entries')
    description = models.CharField(max_length=300, blank=True)
    hours       = models.DecimalField(max_digits=5, decimal_places=2)
    date        = models.DateField()
    is_billable = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.email} — {self.hours}h on {self.date}"