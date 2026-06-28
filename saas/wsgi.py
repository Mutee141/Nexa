"""
WSGI config for saas project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saas.settings')

# Auto-migrate on startup for Render (since default build commands often miss it)
try:
    print("Checking for pending database migrations...")
    call_command('migrate', interactive=False)
    print("Database migrations complete.")
except Exception as e:
    print(f"Error during auto-migration: {e}")

application = get_wsgi_application()
