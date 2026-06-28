import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saas.settings')
django.setup()
from django.test import Client
from accounts.models import User
from django.contrib.auth.hashers import make_password

email = 'testuser@example.com'
password = 'TestPass123!'
user, created = User.objects.get_or_create(
    email=email,
    defaults={'username': 'testuser', 'password': make_password(password)}
)
if created:
    user.first_name = 'Test'
    user.last_name = 'User'
    user.save()

client = Client()
client.force_login(user)
response = client.get('/dashboard/')
print('status_code:', response.status_code)
print('content_start:')
print(response.content.decode('utf-8')[:1200])
