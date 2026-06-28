from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SlackSettings


@login_required
def slack_settings_page(request):
    settings_obj, _ = SlackSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        settings_obj.channel_id      = request.POST.get('channel_id', '').strip()
        settings_obj.channel_name    = request.POST.get('channel_name', '').strip()
        settings_obj.is_enabled      = 'is_enabled' in request.POST
        settings_obj.notify_tasks    = 'notify_tasks' in request.POST
        settings_obj.notify_meetings = 'notify_meetings' in request.POST
        settings_obj.save()
        messages.success(request, 'Slack settings saved!')
        return redirect('slack_settings_page')

    return render(request, 'slack_integration/settings.html', {'settings': settings_obj})


@login_required
def test_slack(request):
    if request.method == 'POST':
        from .utils import send_slack_message
        settings_obj, _ = SlackSettings.objects.get_or_create(user=request.user)
        if settings_obj.channel_id:
            ok = send_slack_message(settings_obj.channel_id, ':wave: This is a test message from NexaOps!')
            if ok:
                messages.success(request, 'Test message sent! Check your Slack channel.')
            else:
                messages.error(request, 'Failed to send. Check your Slack token and channel ID.')
        else:
            messages.error(request, 'Please set a channel ID first.')
    return redirect('slack_settings_page')