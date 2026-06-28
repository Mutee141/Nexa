from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'role', 'is_staff', 'is_active', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active', 'is_superuser')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('avatar', 'job_title', 'phone', 'bio', 'role')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile', {
            'fields': ('email', 'avatar', 'job_title', 'phone', 'bio', 'role')
        }),
    )
