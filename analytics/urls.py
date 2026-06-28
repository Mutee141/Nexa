from django.urls import path
from . import views

urlpatterns = [
    path('',              views.analytics_dashboard, name='analytics_dashboard'),
    path('ai-report/',    views.ai_monthly_report,   name='ai_monthly_report'),
]