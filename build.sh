#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create a default superuser (optional, requires DJANGO_SUPERUSER_PASSWORD, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_USERNAME to be set in Render environment)
# python manage.py createsuperuser --noinput || true
