from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta, date
import json

from tasks.models import Task, Project
from employees.models import Employee
from meetings.models import Meeting
from documents.models import Document
from accounts.models import User


def get_last_7_days():
    today = date.today()
    return [(today - timedelta(days=i)) for i in range(6, -1, -1)]


def get_last_6_months():
    today = date.today()
    months = []
    for i in range(5, -1, -1):
        month = today.month - i
        year  = today.year
        while month <= 0:
            month += 12
            year  -= 1
        months.append((year, month))
    return months


@login_required
def analytics_dashboard(request):
    today     = date.today()
    this_week = today - timedelta(days=7)
    this_month_start = today.replace(day=1)

    # ---- Top KPI cards ----
    total_tasks      = Task.objects.count()
    completed_tasks  = Task.objects.filter(status='done').count()
    overdue_tasks    = Task.objects.filter(
        due_date__lt=today, status__in=['todo', 'in_progress', 'review']
    ).count()
    completion_rate  = round((completed_tasks / total_tasks * 100) if total_tasks else 0)

    active_projects    = Project.objects.filter(status='active').count()
    completed_projects = Project.objects.filter(status='completed').count()
    total_employees    = Employee.objects.count()
    active_employees   = Employee.objects.filter(status='active').count()
    meetings_this_month = Meeting.objects.filter(
        start_time__date__gte=this_month_start
    ).count()
    total_documents = Document.objects.count()

    # ---- Tasks by status (donut chart) ----
    task_status_data = {
        'labels': ['To Do', 'In Progress', 'In Review', 'Done'],
        'data': [
            Task.objects.filter(status='todo').count(),
            Task.objects.filter(status='in_progress').count(),
            Task.objects.filter(status='review').count(),
            Task.objects.filter(status='done').count(),
        ],
        'colors': ['#94a3b8', '#6366f1', '#f59e0b', '#10b981'],
    }

    # ---- Tasks by priority (bar chart) ----
    task_priority_data = {
        'labels': ['Low', 'Medium', 'High', 'Critical'],
        'data': [
            Task.objects.filter(priority='low').count(),
            Task.objects.filter(priority='medium').count(),
            Task.objects.filter(priority='high').count(),
            Task.objects.filter(priority='critical').count(),
        ],
        'colors': ['#94a3b8', '#6366f1', '#f59e0b', '#ef4444'],
    }

    # ---- Tasks completed last 7 days (line chart) ----
    days      = get_last_7_days()
    daily_completed = []
    daily_created   = []
    day_labels      = []
    for d in days:
        daily_completed.append(
            Task.objects.filter(status='done', updated_at__date=d).count()
        )
        daily_created.append(
            Task.objects.filter(created_at__date=d).count()
        )
        day_labels.append(d.strftime('%b %d'))

    weekly_chart = {
        'labels':    day_labels,
        'completed': daily_completed,
        'created':   daily_created,
    }

    # ---- Monthly task completion (last 6 months) ----
    months      = get_last_6_months()
    month_data  = []
    month_labels = []
    for year, month in months:
        count = Task.objects.filter(
            status='done',
            updated_at__year=year,
            updated_at__month=month,
        ).count()
        month_data.append(count)
        month_labels.append(date(year, month, 1).strftime('%b %Y'))

    monthly_chart = {
        'labels': month_labels,
        'data':   month_data,
    }

    # ---- Top performers (employees with most completed tasks) ----
    top_performers = User.objects.annotate(
        completed=Count('assigned_tasks', filter=Q(assigned_tasks__status='done')),
        total=Count('assigned_tasks'),
    ).filter(total__gt=0).order_by('-completed')[:5]

    # ---- Project health ----
    projects = Project.objects.annotate(
        total_tasks=Count('tasks'),
        done_tasks=Count('tasks', filter=Q(tasks__status='done')),
    ).order_by('-created_at')[:6]

    # ---- Recent activity ----
    recent_tasks = Task.objects.select_related(
        'assigned_to', 'created_by'
    ).order_by('-updated_at')[:8]

    context = {
        # KPIs
        'total_tasks':      total_tasks,
        'completed_tasks':  completed_tasks,
        'overdue_tasks':    overdue_tasks,
        'completion_rate':  completion_rate,
        'active_projects':  active_projects,
        'completed_projects': completed_projects,
        'total_employees':  total_employees,
        'active_employees': active_employees,
        'meetings_this_month': meetings_this_month,
        'total_documents':  total_documents,

        # Charts (as JSON)
        'task_status_json':   json.dumps(task_status_data),
        'task_priority_json': json.dumps(task_priority_data),
        'weekly_chart_json':  json.dumps(weekly_chart),
        'monthly_chart_json': json.dumps(monthly_chart),

        # Tables
        'top_performers': top_performers,
        'projects':       projects,
        'recent_tasks':   recent_tasks,
    }
    return render(request, 'analytics/dashboard.html', context)


@login_required
def ai_monthly_report(request):
    """AI generates a monthly performance report"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        import anthropic
        from django.conf import settings

        today = date.today()
        month_start = today.replace(day=1)

        # Gather real data
        total_tasks     = Task.objects.count()
        done_tasks      = Task.objects.filter(status='done').count()
        overdue_tasks   = Task.objects.filter(
            due_date__lt=today, status__in=['todo','in_progress','review']
        ).count()
        new_projects    = Project.objects.filter(
            created_at__date__gte=month_start
        ).count()
        meetings_held   = Meeting.objects.filter(
            start_time__date__gte=month_start,
            status='completed'
        ).count()
        active_emps     = Employee.objects.filter(status='active').count()
        docs_uploaded   = Document.objects.filter(
            created_at__date__gte=month_start
        ).count()
        completion_rate = round((done_tasks / total_tasks * 100) if total_tasks else 0)

        top_user = User.objects.annotate(
            completed=Count('assigned_tasks', filter=Q(assigned_tasks__status='done'))
        ).order_by('-completed').first()

        prompt = f"""
You are a professional business analyst. Write a concise monthly performance report for a company using NexaOps platform.

Data for {today.strftime('%B %Y')}:
- Total tasks: {total_tasks} | Completed: {done_tasks} | Overdue: {overdue_tasks}
- Completion rate: {completion_rate}%
- New projects started this month: {new_projects}
- Meetings completed: {meetings_held}
- Active employees: {active_emps}
- Documents uploaded: {docs_uploaded}
- Top performer: {top_user.get_full_name() or top_user.email if top_user else 'N/A'} ({top_user.assigned_tasks.filter(status='done').count() if top_user else 0} tasks completed)

Write a professional monthly report with:
1. Executive Summary (2-3 sentences)
2. Key Achievements
3. Areas of Concern
4. Recommendations for next month

Keep it concise, professional, and actionable. Use bullet points.
"""
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=800,
            system="You are a professional business analyst writing monthly performance reports.",
            messages=[{'role': 'user', 'content': prompt}],
        )
        report = response.content[0].text
        return JsonResponse({'report': report, 'month': today.strftime('%B %Y')})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)