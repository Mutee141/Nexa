from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='dashboard_home'),
    path('calendar/', views.calendar_view, name='calendar_view'),
]