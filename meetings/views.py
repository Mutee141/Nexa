from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Meeting
from accounts.models import User
from notifications.utils import notify_meeting_created
from slack_integration.utils import notify_slack_meeting

@login_required
def meeting_list(request):
    meetings = Meeting.objects.prefetch_related('attendees').order_by('-start_time')

    status = request.GET.get('status')
    if status:
        meetings = meetings.filter(status=status)

    context = {
        'meetings':   meetings,
        'total':      Meeting.objects.count(),
        'scheduled':  Meeting.objects.filter(status='scheduled').count(),
        'completed':  Meeting.objects.filter(status='completed').count(),
        'cancelled':  Meeting.objects.filter(status='cancelled').count(),
        'selected_status': status or '',
    }
    return render(request, 'meetings/meeting_list.html', context)


@login_required
def meeting_create(request):
    if request.method == 'POST':
        title        = request.POST.get('title', '')
        description  = request.POST.get('description', '')
        start_time   = request.POST.get('start_time')
        end_time     = request.POST.get('end_time')
        location     = request.POST.get('location', '')
        meeting_link = request.POST.get('meeting_link', '')
        attendee_ids = request.POST.getlist('attendees')

        if not title or not start_time or not end_time:
            messages.error(request, 'Title, start time and end time are required.')
            return redirect('meeting_create')

        meeting = Meeting.objects.create(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            meeting_link=meeting_link,
            organizer=request.user,
            status='scheduled',
        )
        if attendee_ids:
            meeting.attendees.set(attendee_ids)
        notify_meeting_created(meeting)
        notify_slack_meeting(meeting)

        messages.success(request, f'Meeting "{title}" scheduled!')
        return redirect('meeting_list')

    context = {'users': User.objects.all()}
    return render(request, 'meetings/meeting_form.html', context)


@login_required
def meeting_edit(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)

    if request.method == 'POST':
        meeting.title        = request.POST.get('title', meeting.title)
        meeting.description  = request.POST.get('description', '')
        meeting.start_time   = request.POST.get('start_time')
        meeting.end_time     = request.POST.get('end_time')
        meeting.location     = request.POST.get('location', '')
        meeting.meeting_link = request.POST.get('meeting_link', '')
        meeting.status       = request.POST.get('status', meeting.status)
        meeting.notes        = request.POST.get('notes', '')
        attendee_ids         = request.POST.getlist('attendees')
        meeting.save()
        meeting.attendees.set(attendee_ids)
        messages.success(request, f'Meeting "{meeting.title}" updated!')
        return redirect('meeting_list')

    context = {
        'meeting': meeting,
        'users':   User.objects.all(),
        'start_fmt': meeting.start_time.strftime('%Y-%m-%dT%H:%M'),
        'end_fmt':   meeting.end_time.strftime('%Y-%m-%dT%H:%M'),
    }
    return render(request, 'meetings/meeting_form.html', context)


@login_required
def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    return render(request, 'meetings/meeting_detail.html', {'meeting': meeting})


@login_required
def meeting_delete(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        name = meeting.title
        meeting.delete()
        messages.success(request, f'Meeting "{name}" deleted.')
    return redirect('meeting_list')


@login_required
def meeting_summarize(request, pk):
    """AI summarize meeting notes"""
    import anthropic, json
    from django.conf import settings
    from django.http import JsonResponse

    meeting = get_object_or_404(Meeting, pk=pk)

    if request.method == 'POST':
        try:
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            content = meeting.notes or meeting.description or meeting.title

            response = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=400,
                system="You are a professional meeting analyst. Create clear, concise meeting summaries with key points and action items.",
                messages=[{
                    'role': 'user',
                    'content': (
                        f"Summarize this meeting:\n"
                        f"Title: {meeting.title}\n"
                        f"Date: {meeting.start_time.strftime('%B %d, %Y')}\n"
                        f"Notes: {content}\n\n"
                        f"Provide: 1) Brief summary 2) Key decisions 3) Action items"
                    )
                }],
            )
            summary = response.content[0].text
            meeting.ai_summary = summary
            meeting.save()
            return JsonResponse({'summary': summary})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'POST required'}, status=405)