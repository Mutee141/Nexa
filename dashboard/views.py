from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from tasks.models import Task, Project
from employees.models import Employee
from meetings.models import Meeting


@login_required
def home(request):
    today = timezone.now().date()
    context = {
        'total_tasks':     Task.objects.count(),
        'done_tasks':      Task.objects.filter(status='done').count(),
        'total_projects':  Project.objects.count(),
        'total_employees': Employee.objects.count(),
        'meetings_today':  Meeting.objects.filter(start_time__date=today).count(),
        'recent_tasks':    Task.objects.select_related('assigned_to').order_by('-created_at')[:6],
    }
    return render(request, 'dashboard/home.html', context)