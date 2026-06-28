from django.contrib import admin
from .models import Notification, NotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notif_type', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'notif_type')
    search_fields = ('recipient__email', 'title', 'message')
    readonly_fields = ('created_at',)

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'task_assigned', 'task_due', 'task_completed', 'project_update', 'meeting_reminder', 'meeting_created')
    list_filter = ('task_assigned', 'task_due', 'task_completed')
    search_fields = ('user__email',)
    