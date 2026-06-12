from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.meeting_list,      name='meeting_list'),
    path('create/',                 views.meeting_create,    name='meeting_create'),
    path('<int:pk>/',               views.meeting_detail,    name='meeting_detail'),
    path('<int:pk>/edit/',          views.meeting_edit,      name='meeting_edit'),
    path('<int:pk>/delete/',        views.meeting_delete,    name='meeting_delete'),
    path('<int:pk>/summarize/',     views.meeting_summarize, name='meeting_summarize'),
]