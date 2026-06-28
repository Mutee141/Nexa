from rest_framework import serializers
from tasks.models import Task, Project
from employees.models import Employee, Department
from meetings.models import Meeting
from documents.models import Document
from accounts.models import User


class UserMiniSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'job_title']

    def get_full_name(self, obj):
        return obj.get_full_name()


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    project_name      = serializers.CharField(source='project.name', read_only=True)
    status_display    = serializers.CharField(source='get_status_display', read_only=True)
    priority_display  = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'priority', 'priority_display', 'project', 'project_name',
            'assigned_to', 'assigned_to_name', 'due_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    owner_name     = serializers.CharField(source='owner.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    task_count     = serializers.IntegerField(source='tasks.count', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'status', 'status_display',
            'priority', 'owner', 'owner_name', 'start_date', 'end_date',
            'task_count', 'created_at',
        ]


class EmployeeSerializer(serializers.ModelSerializer):
    name       = serializers.CharField(source='user.get_full_name', read_only=True)
    email      = serializers.CharField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'name', 'email', 'employee_id', 'department', 'department_name',
            'status', 'date_of_joining',
        ]


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.IntegerField(source='employees.count', read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'employee_count']


class MeetingSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)

    class Meta:
        model = Meeting
        fields = [
            'id', 'title', 'description', 'status', 'organizer', 'organizer_name',
            'start_time', 'end_time', 'location', 'meeting_link',
        ]


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_url         = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'description', 'category', 'file_url',
            'uploaded_by', 'uploaded_by_name', 'created_at',
        ]

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None