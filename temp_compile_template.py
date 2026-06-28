import os
import django
from django.template import loader, TemplateSyntaxError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saas.settings')
django.setup()
try:
    tpl = loader.get_template('dashboard/home.html')
    print('template loaded successfully')
except Exception as e:
    print(type(e).__name__)
    print(e)
