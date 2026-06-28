from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from tasks.models import Project, Task
from accounts.models import User
from audit.utils import log_action


@login_required
def project_list(request):
    projects = Project.objects.prefetch_related('members', 'tasks').annotate(
        tasks_done_count=Count('tasks', filter=Q(tasks__status='done'))
    ).order_by('-created_at')

    status = request.GET.get('status')
    if status:
        projects = projects.filter(status=status)

    context = {
        'projects':    projects,
        'total':       Project.objects.count(),
        'active':      Project.objects.filter(status='active').count(),
        'completed':   Project.objects.filter(status='completed').count(),
        'planning':    Project.objects.filter(status='planning').count(),
        'selected_status': status or '',
    }
    return render(request, 'projects/project_list.html', context)


@login_required
def project_create(request):
    if request.method == 'POST':
        name        = request.POST.get('name')
        description = request.POST.get('description', '')
        status      = request.POST.get('status', 'planning')
        priority    = request.POST.get('priority', 'medium')
        start_date  = request.POST.get('start_date') or None
        end_date    = request.POST.get('end_date') or None
        member_ids  = request.POST.getlist('members')

        if not name:
            messages.error(request, 'Project name is required.')
            return redirect('project_create')

        project = Project.objects.create(
            name=name,
            description=description,
            status=status,
            priority=priority,
            start_date=start_date,
            end_date=end_date,
            owner=request.user,
        )
        log_action(request, 'create', 'Project', project.name, project.pk)
        if member_ids:
            project.members.set(member_ids)

        messages.success(request, f'Project "{project.name}" created!')
        return redirect('project_list')

    context = {'users': User.objects.all()}
    return render(request, 'projects/project_form.html', context)


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        project.name        = request.POST.get('name')
        project.description = request.POST.get('description', '')
        project.status      = request.POST.get('status', 'planning')
        project.priority    = request.POST.get('priority', 'medium')
        project.start_date  = request.POST.get('start_date') or None
        project.end_date    = request.POST.get('end_date') or None
        member_ids          = request.POST.getlist('members')
        project.save()
        log_action(request, 'update', 'Project', project.name, project.pk)
        project.members.set(member_ids)
        messages.success(request, f'Project "{project.name}" updated!')
        return redirect('project_list')

    context = {
        'project': project,
        'users':   User.objects.all(),
    }
    return render(request, 'projects/project_form.html', context)


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    tasks   = Task.objects.filter(project=project).select_related('assigned_to')
    context = {
        'project':      project,
        'tasks':        tasks,
        'total_tasks':  tasks.count(),
        'done_tasks':   tasks.filter(status='done').count(),
        'active_tasks': tasks.filter(status='in_progress').count(),
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        name = project.name
        log_action(request, 'delete', 'Project', name, pk)
        project.delete()
        messages.success(request, f'Project "{name}" deleted.')
    return redirect('project_list')

@login_required
def project_gantt(request, pk):
    project = get_object_or_404(Project, pk=pk)
    tasks   = project.tasks.exclude(due_date__isnull=True).order_by('due_date')

    import json
    gantt_data = []
    for task in tasks:
        start = task.created_at.date()
        end   = task.due_date

        if end < start:
            end = start

        gantt_data.append({
            'id':       task.pk,
            'name':     task.title,
            'start':    start.isoformat(),
            'end':      end.isoformat(),
            'progress': 100 if task.status == 'done' else (60 if task.status == 'in_progress' else (30 if task.status == 'review' else 0)),
            'status':   task.get_status_display(),
        })

    return render(request, 'projects/gantt.html', {
        'project': project,
        'gantt_json': json.dumps(gantt_data),
        'has_tasks': len(gantt_data) > 0,
    })