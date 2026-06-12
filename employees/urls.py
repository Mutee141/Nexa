from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.employee_list,     name='employee_list'),
    path('create/',                 views.employee_create,   name='employee_create'),
    path('<int:pk>/',               views.employee_detail,   name='employee_detail'),
    path('<int:pk>/edit/',          views.employee_edit,     name='employee_edit'),
    path('<int:pk>/delete/',        views.employee_delete,   name='employee_delete'),
    path('departments/',            views.department_list,   name='department_list'),
    path('departments/create/',     views.department_create, name='department_create'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
]