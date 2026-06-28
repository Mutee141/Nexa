# dashboard/views.py  — replace your existing file with this

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
        # Top KPI cards
        'total_tasks':      Task.objects.count(),
        'done_tasks':       Task.objects.filter(status='done').count(),
        'total_projects':   Project.objects.count(),
        'total_employees':  Employee.objects.count(),
        'meetings_today':   Meeting.objects.filter(start_time__date=today).count(),

        # Donut chart breakdown
        'todo_count':       Task.objects.filter(status='todo').count(),
        'inprogress_count': Task.objects.filter(status='in_progress').count(),
        'review_count':     Task.objects.filter(status='review').count(),

        # Recent tasks (activity + task list)
        'recent_tasks':     Task.objects.select_related('assigned_to', 'project').order_by('-updated_at')[:8],
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def calendar_view(request):
    from tasks.models import Task
    from meetings.models import Meeting
    import json

    tasks    = Task.objects.filter(due_date__isnull=False).select_related('project')
    meetings = Meeting.objects.filter(status='scheduled').select_related('organizer')

    events = []

    for task in tasks:
        events.append({
            'id':    f'task-{task.pk}',
            'title': task.title,
            'start': str(task.due_date),
            'url':   f'/tasks/{task.pk}/',
            'color': '#6366f1' if task.priority == 'critical' else
                     '#f59e0b' if task.priority == 'high' else
                     '#6366f1',
            'type':  'task',
        })

    for meeting in meetings:
        events.append({
            'id':    f'meeting-{meeting.pk}',
            'title': f'📹 {meeting.title}',
            'start': meeting.start_time.isoformat(),
            'end':   meeting.end_time.isoformat(),
            'url':   f'/meetings/{meeting.pk}/',
            'color': '#059669',
            'type':  'meeting',
        })

    return render(request, 'dashboard/calendar.html', {
        'events': events
    })