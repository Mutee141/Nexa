from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task, Project
from accounts.models import User


@login_required
def task_list(request):
    tasks = Task.objects.select_related('assigned_to', 'project').order_by('-created_at')

    # Filter by status
    status = request.GET.get('status')
    if status:
        tasks = tasks.filter(status=status)

    # Filter by priority
    priority = request.GET.get('priority')
    if priority:
        tasks = tasks.filter(priority=priority)

    context = {
        'tasks':        tasks,
        'total':        Task.objects.count(),
        'todo':         Task.objects.filter(status='todo').count(),
        'in_progress':  Task.objects.filter(status='in_progress').count(),
        'done':         Task.objects.filter(status='done').count(),
        'selected_status':   status or '',
        'selected_priority': priority or '',
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_create(request):
    if request.method == 'POST':
        title       = request.POST.get('title')
        description = request.POST.get('description', '')
        priority    = request.POST.get('priority', 'medium')
        status      = request.POST.get('status', 'todo')
        due_date    = request.POST.get('due_date') or None
        assigned_id = request.POST.get('assigned_to') or None
        project_id  = request.POST.get('project') or None

        if not title:
            messages.error(request, 'Task title is required.')
            return redirect('task_create')

        task = Task.objects.create(
            title=title,
            description=description,
            priority=priority,
            status=status,
            due_date=due_date,
            assigned_to_id=assigned_id,
            project_id=project_id,
            created_by=request.user,
        )
        messages.success(request, f'Task "{task.title}" created successfully!')
        return redirect('task_list')

    context = {
        'users':    User.objects.all(),
        'projects': Project.objects.all(),
    }
    return render(request, 'tasks/task_form.html', context)


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        task.title       = request.POST.get('title')
        task.description = request.POST.get('description', '')
        task.priority    = request.POST.get('priority', 'medium')
        task.status      = request.POST.get('status', 'todo')
        task.due_date    = request.POST.get('due_date') or None
        assigned_id      = request.POST.get('assigned_to') or None
        project_id       = request.POST.get('project') or None
        task.assigned_to_id = assigned_id
        task.project_id     = project_id
        task.save()
        messages.success(request, f'Task "{task.title}" updated!')
        return redirect('task_list')

    context = {
        'task':     task,
        'users':    User.objects.all(),
        'projects': Project.objects.all(),
    }
    return render(request, 'tasks/task_form.html', context)


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        name = task.title
        task.delete()
        messages.success(request, f'Task "{name}" deleted.')
    return redirect('task_list')


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/task_detail.html', {'task': task})