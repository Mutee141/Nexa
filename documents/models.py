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

    def get_file_extension(self):
        """Return the uppercase file extension (e.g. 'PDF', 'DOCX')."""
        import os
        if self.file:
            _, ext = os.path.splitext(self.file.name)
            return ext.lstrip('.').upper()
        return ''

    def get_file_size(self):
        """Return a human-readable file size string (e.g. '1.2 MB')."""
        try:
            size = self.file.size
            if size < 1024:
                return f'{size} B'
            elif size < 1024 ** 2:
                return f'{size / 1024:.1f} KB'
            else:
                return f'{size / 1024 ** 2:.1f} MB'
        except Exception:
            return ''

    class Meta:
        ordering = ['-created_at']