from django.urls import path
from . import views

urlpatterns = [
    path('',               views.timesheet,    name='timesheet'),
    path('log/',           views.log_time,     name='log_time'),
    path('<int:pk>/delete/', views.delete_entry, name='delete_time_entry'),
]