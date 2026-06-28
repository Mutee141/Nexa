from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('tasks',       views.TaskViewSet,       basename='task')
router.register('projects',    views.ProjectViewSet,    basename='project')
router.register('employees',   views.EmployeeViewSet,   basename='employee')
router.register('departments', views.DepartmentViewSet, basename='department')
router.register('meetings',    views.MeetingViewSet,    basename='meeting')
router.register('documents',   views.DocumentViewSet,   basename='document')

urlpatterns = [
    path('', include(router.urls)),
]