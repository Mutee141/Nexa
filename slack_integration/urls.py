from django.urls import path
from . import views

urlpatterns = [
    path('',      views.slack_settings_page, name='slack_settings_page'),
    path('test/', views.test_slack,          name='test_slack'),
]