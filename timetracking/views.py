from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import TimeEntry
from tasks.models import Task, Project
from accounts.models import User
from datetime import timedelta, date


@login_required
def timesheet(request):
    entries = TimeEntry.objects.filter(user=request.user).select_related('task', 'project')

    # Week filter
    week_start = date.today() - timedelta(days=date.today().weekday())
    week_end   = week_start + timedelta(days=6)

    week_entries  = entries.filter(date__range=[week_start, week_end])
    total_hours   = entries.aggregate(t=Sum('hours'))['t'] or 0
    week_hours    = week_entries.aggregate(t=Sum('hours'))['t'] or 0
    billable_hours= entries.filter(is_billable=True).aggregate(t=Sum('hours'))['t'] or 0

    context = {
        'entries':        entries[:50],
        'total_hours':    total_hours,
        'week_hours':     week_hours,
        'billable_hours': billable_hours,
        'tasks':          Task.objects.all(),
        'projects':       Project.objects.all(),
    }
    return render(request, 'timetracking/timesheet.html', context)


@login_required
def log_time(request):
    if request.method == 'POST':
        task_id     = request.POST.get('task') or None
        project_id  = request.POST.get('project') or None
        hours       = request.POST.get('hours', 0)
        desc        = request.POST.get('description', '')
        entry_date  = request.POST.get('date') or date.today()
        is_billable = 'is_billable' in request.POST

        if not hours or float(hours) <= 0:
            messages.error(request, 'Please enter valid hours.')
            return redirect('timesheet')

        entry = TimeEntry.objects.create(
            user=request.user,
            task_id=task_id,
            project_id=project_id,
            hours=hours,
            description=desc,
            date=entry_date,
            is_billable=is_billable,
        )
        messages.success(request, f'Logged {hours} hours successfully!')
        return redirect('timesheet')

    return redirect('timesheet')


@login_required
def delete_entry(request, pk):
    entry = get_object_or_404(TimeEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Time entry deleted.')
    return redirect('timesheet')