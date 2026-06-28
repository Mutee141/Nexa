from django.urls import path
from . import views

urlpatterns = [
    path('',              views.task_list,   name='task_list'),
    path('create/',       views.task_create, name='task_create'),
    path('<int:pk>/',     views.task_detail, name='task_detail'),
    path('<int:pk>/edit/',   views.task_edit,   name='task_edit'),
    path('<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('kanban/',         views.kanban_board,       name='kanban_board'),
    path('<int:pk>/status/',views.task_update_status,name='task_update_status'),
    path('<int:task_pk>/comment/',          views.add_comment,    name='add_comment'),
    path('comment/<int:pk>/delete/',        views.delete_comment, name='delete_comment'),
    path('export/excel/', views.export_tasks_excel, name='export_tasks_excel'),
    path('export/pdf/',   views.export_tasks_pdf,   name='export_tasks_pdf'),
]