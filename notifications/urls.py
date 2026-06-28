from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('count/', views.notification_count, name='notification_count'),
    path('dropdown/', views.notification_dropdown, name='notification_dropdown'),
    path('<int:pk>/mark-read/', views.mark_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('clear-all/', views.clear_all, name='clear_all'),
    path('preferences/', views.notification_preferences, name='notification_preferences'),
]
