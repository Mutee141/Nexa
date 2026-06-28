from django.shortcuts import render

# Create your views here.
import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from documents.models import Document
import g4f

# Use g4f directly instead of OpenAI to automatically use free providers and avoid quota issues



@login_required
def assistant(request):
    quick_prompts = []  # We handle these in the template directly
    return render(request, 'ai/assistant.html', {'quick_prompts': quick_prompts})


@login_required
def chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data       = json.loads(request.body)
        user_msg   = data.get('message', '').strip()
        history    = data.get('history', [])

        if not user_msg:
            return JsonResponse({'error': 'Empty message'}, status=400)

        # Build messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": (
                    "You are NexaOps AI Assistant — a smart, helpful business operations assistant. "
                    "You help teams with tasks, projects, meetings, emails, reports, and general business questions. "
                    "Be concise, professional, and practical. Format responses clearly using bullet points or numbered lists when appropriate."
                )
            }
        ]

        # Add conversation history (last 10 messages)
        for msg in history[-10:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        # Add current message
        messages.append({"role": "user", "content": user_msg})

        response = g4f.ChatCompletion.create(
            model=g4f.models.default,
            messages=messages,
        )

        reply = response
        return JsonResponse({'reply': reply})

    except Exception as e:
        return JsonResponse({'error': 'Service is currently busy or unavailable. Please try again in a few moments.'}, status=500)


@login_required
def email_writer(request):
    result = None
    if request.method == 'POST':
        purpose   = request.POST.get('purpose', '')
        recipient = request.POST.get('recipient', '')
        tone      = request.POST.get('tone', 'professional')
        details   = request.POST.get('details', '')

        prompt = (
            f"Write a {tone} business email.\n"
            f"Purpose: {purpose}\n"
            f"Recipient: {recipient}\n"
            f"Key details: {details}\n\n"
            f"Write a complete email with subject line, greeting, body, and sign-off. "
            f"Format: start with 'Subject: ...' on the first line."
        )

        try:
            response = g4f.ChatCompletion.create(
                model=g4f.models.default,
                messages=[
                    {"role": "system", "content": "You are a professional business email writer."},
                    {"role": "user",   "content": prompt}
                ]
            )
            result = response
        except Exception as e:
            result = "We're experiencing high demand right now or a service disruption. Please try again in a few moments."

    return render(request, 'ai/email_writer.html', {'result': result})


@login_required
def task_generator(request):
    result = None
    if request.method == 'POST':
        goal    = request.POST.get('goal', '')
        context = request.POST.get('context', '')

        prompt = (
            f"Break down this business goal into specific, actionable tasks.\n"
            f"Goal: {goal}\n"
            f"Context: {context}\n\n"
            f"Return a numbered list of 5-8 specific tasks. "
            f"For each task include: task name, priority (High/Medium/Low), and estimated time."
        )

        try:
            response = g4f.ChatCompletion.create(
                model=g4f.models.default,
                messages=[
                    {"role": "system", "content": "You are a professional project manager who breaks down goals into actionable tasks."},
                    {"role": "user",   "content": prompt}
                ]
            )
            result = response
        except Exception as e:
            result = "We're experiencing high demand right now or a service disruption. Please try again in a few moments."

    return render(request, 'ai/task_generator.html', {'result': result})


@login_required
def summarize_doc(request, doc_id):
    document = get_object_or_404(Document, pk=doc_id)

    if request.method == 'POST':
        try:
            # Read up to 3000 chars from the document description as sample
            content = document.description or document.title

            response = g4f.ChatCompletion.create(
                model=g4f.models.default,
                messages=[
                    {"role": "system", "content": "You are a document analyst. Summarize business documents clearly and concisely."},
                    {"role": "user",   "content": f"Summarize this document:\nTitle: {document.title}\nContent: {content}"}
                ]
            )
            summary = response
            document.ai_summary = summary
            document.save()
            return JsonResponse({'summary': summary})
        except Exception as e:
            return JsonResponse({'error': "We're experiencing high demand right now. Please try again in a few moments."}, status=500)

    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
def daily_standup(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        from django.utils import timezone
        from datetime import timedelta
        from tasks.models import Task

        today     = timezone.now().date()
        yesterday = today - timedelta(days=1)

        # Gather real data for this user
        done_yesterday  = Task.objects.filter(
            assigned_to=request.user,
            status='done',
            updated_at__date=yesterday
        )
        today_tasks     = Task.objects.filter(
            assigned_to=request.user,
            status__in=['todo', 'in_progress'],
            due_date=today
        )
        overdue_tasks   = Task.objects.filter(
            assigned_to=request.user,
            status__in=['todo', 'in_progress'],
            due_date__lt=today
        )
        in_progress     = Task.objects.filter(
            assigned_to=request.user,
            status='in_progress'
        )

        # Build prompt with real data
        done_list     = '\n'.join([f'- {t.title}' for t in done_yesterday]) or 'None recorded'
        today_list    = '\n'.join([f'- {t.title} (due today)' for t in today_tasks]) or 'No tasks due today'
        inprog_list   = '\n'.join([f'- {t.title}' for t in in_progress]) or 'None'
        overdue_list  = '\n'.join([f'- {t.title} (overdue)' for t in overdue_tasks]) or 'None'

        prompt = f"""Generate a professional daily standup update for {request.user.get_full_name() or request.user.email}.

Today is {today.strftime('%A, %B %d, %Y')}.

Data from their task management system:

COMPLETED YESTERDAY:
{done_list}

CURRENTLY IN PROGRESS:
{inprog_list}

DUE TODAY:
{today_list}

OVERDUE TASKS:
{overdue_list}

Write a concise standup in this format:
✅ Yesterday: (what was completed)
🔄 Today: (what will be worked on)
🚧 Blockers: (any blockers or risks, based on overdue tasks)

Keep it professional, first-person, under 100 words. If no data exists in a section, write a sensible default."""

        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=400,
            system="You are a professional project manager assistant. Write concise, professional daily standup updates.",
            messages=[{'role': 'user', 'content': prompt}],
        )
        standup = response.content[0].text
        return JsonResponse({'standup': standup, 'date': today.strftime('%B %d, %Y')})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def smart_search(request):
    query   = request.GET.get('q', '').strip()
    results = []
    ai_interpretation = ''

    if query:
        try:
            from tasks.models import Task, Project
            from employees.models import Employee
            from meetings.models import Meeting
            from documents.models import Document

            # Ask AI to interpret the query
            prompt = f"""The user searched for: "{query}"

Extract search filters from this natural language query. Return ONLY a JSON object with these fields:
{{
  "keywords": "main search term",
  "status": "todo|in_progress|review|done|null",
  "priority": "low|medium|high|critical|null",
  "type": "task|project|employee|meeting|document|all",
  "overdue": true|false|null
}}

Examples:
"overdue high priority tasks" → {{"keywords":"","status":null,"priority":"high","type":"task","overdue":true}}
"completed tasks for Ahmed" → {{"keywords":"Ahmed","status":"done","priority":null,"type":"task","overdue":false}}
"marketing project" → {{"keywords":"marketing","status":null,"priority":null,"type":"project","overdue":null}}
"""
            ai_response = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=200,
                system="Return only valid JSON, no explanation, no markdown.",
                messages=[{'role': 'user', 'content': prompt}],
            )

            import json as jsonlib
            raw = ai_response.content[0].text.strip()
            # Clean any markdown
            raw = raw.replace('```json', '').replace('```', '').strip()
            filters = jsonlib.loads(raw)

            keywords  = filters.get('keywords', '')
            f_status  = filters.get('status')
            f_priority= filters.get('priority')
            f_type    = filters.get('type', 'all')
            f_overdue = filters.get('overdue')

            from django.utils import timezone
            today = timezone.now().date()

            # Search Tasks
            if f_type in ['task', 'all']:
                tasks_qs = Task.objects.select_related('project', 'assigned_to').all()
                if keywords:
                    tasks_qs = tasks_qs.filter(title__icontains=keywords) | \
                               tasks_qs.filter(assigned_to__first_name__icontains=keywords) | \
                               tasks_qs.filter(assigned_to__last_name__icontains=keywords)
                if f_status:
                    tasks_qs = tasks_qs.filter(status=f_status)
                if f_priority:
                    tasks_qs = tasks_qs.filter(priority=f_priority)
                if f_overdue:
                    tasks_qs = tasks_qs.filter(due_date__lt=today, status__in=['todo','in_progress','review'])
                for t in tasks_qs.distinct()[:8]:
                    results.append({
                        'type':     'task',
                        'icon':     'fa-list-check',
                        'color':    'indigo',
                        'title':    t.title,
                        'subtitle': f'{t.get_status_display()} · {t.get_priority_display()} priority',
                        'url':      f'/tasks/{t.pk}/',
                        'badge':    t.get_status_display(),
                    })

            # Search Projects
            if f_type in ['project', 'all']:
                proj_qs = Project.objects.all()
                if keywords:
                    proj_qs = proj_qs.filter(name__icontains=keywords) | \
                              proj_qs.filter(description__icontains=keywords)
                if f_status:
                    proj_qs = proj_qs.filter(status=f_status)
                for p in proj_qs.distinct()[:5]:
                    results.append({
                        'type':     'project',
                        'icon':     'fa-diagram-project',
                        'color':    'violet',
                        'title':    p.name,
                        'subtitle': f'{p.get_status_display()} · {p.tasks.count()} tasks',
                        'url':      f'/projects/{p.pk}/',
                        'badge':    p.get_status_display(),
                    })

            # Search Employees
            if f_type in ['employee', 'all'] and keywords:
                emp_qs = Employee.objects.select_related('user', 'department').filter(
                    user__first_name__icontains=keywords
                ) | Employee.objects.filter(
                    user__last_name__icontains=keywords
                ) | Employee.objects.filter(
                    user__email__icontains=keywords
                )
                for e in emp_qs.distinct()[:5]:
                    results.append({
                        'type':     'employee',
                        'icon':     'fa-user',
                        'color':    'emerald',
                        'title':    e.user.get_full_name() or e.user.email,
                        'subtitle': f'{e.user.job_title or "Employee"} · {e.department.name if e.department else "No dept"}',
                        'url':      f'/employees/{e.pk}/',
                        'badge':    e.get_status_display(),
                    })

            # Search Documents
            if f_type in ['document', 'all'] and keywords:
                doc_qs = Document.objects.filter(title__icontains=keywords)[:5]
                for d in doc_qs:
                    results.append({
                        'type':     'document',
                        'icon':     'fa-file',
                        'color':    'amber',
                        'title':    d.title,
                        'subtitle': f'{d.get_category_display()} · {d.get_file_size()}',
                        'url':      '/documents/',
                        'badge':    d.get_category_display(),
                    })

            # Generate summary
            count = len(results)
            ai_interpretation = f'Found {count} result{"s" if count != 1 else ""} for "{query}"'

        except Exception as e:
            ai_interpretation = f'Search error: {str(e)}'

    return render(request, 'ai/search.html', {
        'query':             query,
        'results':           results,
        'ai_interpretation': ai_interpretation,
    })


@login_required
def performance_review(request, employee_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        from employees.models import Employee
        from tasks.models import Task
        from django.db.models import Count, Q

        employee = Employee.objects.select_related('user', 'department').get(pk=employee_id)
        user     = employee.user

        # Gather performance data
        total_assigned  = Task.objects.filter(assigned_to=user).count()
        completed       = Task.objects.filter(assigned_to=user, status='done').count()
        overdue         = Task.objects.filter(
            assigned_to=user,
            status__in=['todo', 'in_progress'],
            due_date__lt=__import__('datetime').date.today()
        ).count()
        in_progress     = Task.objects.filter(assigned_to=user, status='in_progress').count()
        high_priority   = Task.objects.filter(assigned_to=user, priority__in=['high', 'critical']).count()
        projects_count  = user.projects.count()

        completion_rate = round((completed / total_assigned * 100) if total_assigned > 0 else 0)

        recent_tasks = Task.objects.filter(assigned_to=user, status='done').order_by('-updated_at')[:5]
        recent_list  = '\n'.join([f'- {t.title}' for t in recent_tasks]) or 'None'

        prompt = f"""Generate a professional employee performance review for:

Employee: {user.get_full_name() or user.email}
Job Title: {user.job_title or 'Team Member'}
Department: {employee.department.name if employee.department else 'General'}

Performance Data:
- Total tasks assigned: {total_assigned}
- Tasks completed: {completed} ({completion_rate}% completion rate)
- Currently in progress: {in_progress}
- Overdue tasks: {overdue}
- High/critical priority tasks handled: {high_priority}
- Projects involved in: {projects_count}

Recent completed work:
{recent_list}

Write a balanced, professional performance review with these sections:
1. **Overall Performance Summary** (2-3 sentences)
2. **Key Strengths** (3 bullet points)
3. **Areas for Improvement** (2 bullet points)
4. **Recommendations** (2 bullet points)

Be specific, constructive, and professional. Base insights on the data provided."""

        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=600,
            system="You are an experienced HR manager writing professional performance reviews.",
            messages=[{'role': 'user', 'content': prompt}],
        )
        review = response.content[0].text
        return JsonResponse({
            'review': review,
            'employee': user.get_full_name() or user.email,
            'completion_rate': completion_rate,
            'completed': completed,
            'total': total_assigned,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def risk_detector(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        from tasks.models import Task, Project
        from employees.models import Employee
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        risks = []

        # Risk 1: Overdue tasks
        overdue_tasks = Task.objects.filter(
            due_date__lt=today,
            status__in=['todo', 'in_progress', 'review']
        ).select_related('assigned_to', 'project')[:10]

        for task in overdue_tasks:
            days_overdue = (today - task.due_date).days
            risks.append({
                'level':   'high' if days_overdue > 3 else 'medium',
                'type':    'task_overdue',
                'title':   f'Task overdue by {days_overdue} day{"s" if days_overdue != 1 else ""}',
                'detail':  task.title,
                'assignee':task.assigned_to.get_full_name() if task.assigned_to else 'Unassigned',
                'action':  f'/tasks/{task.pk}/edit/',
                'action_label': 'Update task',
            })

        # Risk 2: Projects with no activity in 7+ days
        stale_cutoff = timezone.now() - timedelta(days=7)
        stale_projects = Project.objects.filter(
            status='active',
            updated_at__lt=stale_cutoff
        )[:5]

        for proj in stale_projects:
            days_stale = (timezone.now() - proj.updated_at).days
            risks.append({
                'level':   'medium',
                'type':    'project_stale',
                'title':   f'No activity for {days_stale} days',
                'detail':  proj.name,
                'assignee':'Project owner: ' + (proj.owner.get_full_name() or proj.owner.email),
                'action':  f'/projects/{proj.pk}/',
                'action_label': 'View project',
            })

        # Risk 3: Critical tasks with no assignee
        unassigned_critical = Task.objects.filter(
            priority__in=['critical', 'high'],
            assigned_to=None,
            status__in=['todo', 'in_progress']
        )[:5]

        for task in unassigned_critical:
            risks.append({
                'level':   'high',
                'type':    'unassigned_critical',
                'title':   f'{task.get_priority_display()} task unassigned',
                'detail':  task.title,
                'assignee':'No one assigned',
                'action':  f'/tasks/{task.pk}/edit/',
                'action_label': 'Assign now',
            })

        # Risk 4: Employees with no tasks
        from django.db.models import Count
        idle_employees = Employee.objects.filter(
            status='active'
        ).annotate(
            active_tasks=Count('user__assigned_tasks', filter=__import__('django.db.models', fromlist=['Q']).Q(user__assigned_tasks__status__in=['todo','in_progress']))
        ).filter(active_tasks=0)[:5]

        for emp in idle_employees:
            risks.append({
                'level':   'low',
                'type':    'idle_employee',
                'title':   'Employee has no active tasks',
                'detail':  emp.user.get_full_name() or emp.user.email,
                'assignee':emp.user.job_title or 'Team member',
                'action':  f'/employees/{emp.pk}/',
                'action_label': 'View profile',
            })

        # Generate AI summary
        risk_count   = len(risks)
        high_count   = sum(1 for r in risks if r['level'] == 'high')
        medium_count = sum(1 for r in risks if r['level'] == 'medium')

        if risk_count == 0:
            ai_summary = "✅ No risks detected! Your workspace is in great shape. All tasks are on track and projects are active."
        else:
            summary_prompt = f"""Analyze these business risks and write a 2-sentence executive summary:
- Total risks: {risk_count}
- High severity: {high_count}
- Medium severity: {medium_count}
- Types: {', '.join(set(r['type'] for r in risks))}

Be direct and actionable. Start with the most critical issue."""

            summary_response = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=150,
                system="You are a business analyst. Be concise and direct.",
                messages=[{'role': 'user', 'content': summary_prompt}],
            )
            ai_summary = summary_response.content[0].text

        return JsonResponse({
            'risks':      risks,
            'count':      risk_count,
            'high':       high_count,
            'medium':     medium_count,
            'ai_summary': ai_summary,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def agenda_builder(request):
    result = None
    if request.method == 'POST':
        goal      = request.POST.get('goal', '')
        duration  = request.POST.get('duration', '60')
        attendees = request.POST.get('attendees', '')
        context_  = request.POST.get('context', '')

        prompt = f"""Create a professional meeting agenda.

Meeting Goal: {goal}
Duration: {duration} minutes
Attendees: {attendees or 'Team members'}
Additional context: {context_ or 'Standard team meeting'}

Generate a detailed meeting agenda with:
1. Meeting title
2. Time-boxed agenda items (with minutes allocated)
3. Owner for each item
4. Expected outcome per item
5. Pre-read materials if needed
6. Action items section at the end

Format clearly with timing like:
[0:00-0:05] Welcome & Objectives (5 min) — Facilitator
[0:05-0:20] ...

Total must equal {duration} minutes exactly."""

        try:
            response = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=600,
                system="You are a professional meeting facilitator. Create clear, time-boxed meeting agendas.",
                messages=[{'role': 'user', 'content': prompt}],
            )
            result = response.content[0].text
        except Exception as e:
            result = f"Error: {str(e)}"

    return render(request, 'ai/agenda_builder.html', {'result': result})

@login_required
def proposal_writer(request):
    from tasks.models import Project
    projects = Project.objects.all()
    result   = None

    if request.method == 'POST':
        project_id   = request.POST.get('project') or None
        client_name  = request.POST.get('client_name', '')
        budget        = request.POST.get('budget', '')
        timeline      = request.POST.get('timeline', '')
        extra_notes   = request.POST.get('notes', '')

        project_info = ''
        if project_id:
            try:
                proj = Project.objects.get(pk=project_id)
                task_list = '\n'.join([f'- {t.title}' for t in proj.tasks.all()[:10]])
                project_info = f"""
Project: {proj.name}
Description: {proj.description or 'Not specified'}
Status: {proj.get_status_display()}
Priority: {proj.get_priority_display()}
Start Date: {proj.start_date or 'TBD'}
End Date: {proj.end_date or 'TBD'}
Tasks:
{task_list or 'No tasks yet'}"""
            except Exception:
                pass

        prompt = f"""Write a professional client proposal for the following:

Client: {client_name or 'Valued Client'}
Budget: {budget or 'To be discussed'}
Timeline: {timeline or 'To be discussed'}
{project_info}
Additional Notes: {extra_notes or 'None'}

Write a complete professional proposal with:
1. **Executive Summary** — Brief overview of what you will deliver
2. **Project Scope** — What is included and what is not
3. **Deliverables** — Specific outputs with clear descriptions
4. **Timeline** — Phased approach with milestones
5. **Investment** — Pricing breakdown
6. **Terms & Conditions** — Brief standard terms
7. **Next Steps** — Clear call to action

Use professional business language. Format with clear sections and bullet points where appropriate."""

        try:
            response = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=1000,
                system="You are a professional business consultant writing client proposals. Be persuasive, clear, and professional.",
                messages=[{'role': 'user', 'content': prompt}],
            )
            result = response.content[0].text
        except Exception as e:
            result = f"Error: {str(e)}"

    return render(request, 'ai/proposal_writer.html', {
        'projects': projects,
        'result':   result,
    })