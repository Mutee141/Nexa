from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from tasks.models import Project, Task


@login_required
def onboarding_wizard(request):
    if request.user.has_completed_onboarding:
        return redirect('dashboard_home')

    step = int(request.GET.get('step', 1))
    context = {'step': step}
    return render(request, 'onboarding/wizard.html', context)


@login_required
def onboarding_step1(request):
    """Step 1: Update name and job title"""
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name  = request.POST.get('last_name', '')
        request.user.job_title  = request.POST.get('job_title', '')
        request.user.save()
        return redirect('/onboarding/?step=2')
    return redirect('onboarding_wizard')


@login_required
def onboarding_step2(request):
    """Step 2: Invite team member (optional)"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            try:
                from invites.models import Invite
                from invites.views import send_invite
                if not Invite.objects.filter(email=email).exists():
                    Invite.objects.create(email=email, role='employee', invited_by=request.user)
                    messages.success(request, f'Invite sent to {email}')
            except Exception:
                pass
        return redirect('/onboarding/?step=3')
    return redirect('onboarding_wizard')


@login_required
def onboarding_step3(request):
    """Step 3: Create first project"""
    if request.method == 'POST':
        name = request.POST.get('project_name', '').strip()
        if name:
            project = Project.objects.create(
                name=name,
                description=request.POST.get('project_description', ''),
                status='planning',
                priority='medium',
                owner=request.user,
            )
            request.session['onboarding_project_id'] = project.pk
        return redirect('/onboarding/?step=4')
    return redirect('onboarding_wizard')


@login_required
def onboarding_step4(request):
    """Step 4: Create first task"""
    if request.method == 'POST':
        title = request.POST.get('task_title', '').strip()
        if title:
            project_id = request.session.get('onboarding_project_id')
            Task.objects.create(
                title=title,
                status='todo',
                priority='medium',
                project_id=project_id,
                assigned_to=request.user,
                created_by=request.user,
            )
        request.user.has_completed_onboarding = True
        request.user.save()
        messages.success(request, 'Welcome to NexaOps! Your workspace is ready.')
        return redirect('dashboard_home')
    return redirect('onboarding_wizard')


@login_required
def skip_onboarding(request):
    request.user.has_completed_onboarding = True
    request.user.save()
    return redirect('dashboard_home')