from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from tasks.models import Task, Project
from employees.models import Employee, Department
from meetings.models import Meeting
from documents.models import Document
from .serializers import (
    TaskSerializer, ProjectSerializer, EmployeeSerializer,
    DepartmentSerializer, MeetingSerializer, DocumentSerializer,
)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related('project', 'assigned_to', 'created_by').all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'project', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'priority']
    search_fields = ['name', 'description']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Employee.objects.select_related('user', 'department').all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'department']


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.select_related('organizer').all()
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.select_related('uploaded_by').all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}