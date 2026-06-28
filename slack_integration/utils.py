from django.conf import settings
from slack_sdk import WebClient

from .models import SlackSettings


def send_slack_message(channel_id, text, blocks=None):
    """Send a simple Slack message if the token and channel are available."""
    token = getattr(settings, 'SLACK_BOT_TOKEN', '')
    if not token or not channel_id:
        return False

    try:
        client = WebClient(token=token)
        payload = {
            'channel': channel_id,
            'text': text,
        }
        if blocks:
            payload['blocks'] = blocks
        response = client.chat_postMessage(**payload)
        return bool(response.get('ok', False))
    except Exception:
        return False


def _notify_enabled_channels(notify_flag, text, blocks=None):
    for settings_obj in SlackSettings.objects.filter(is_enabled=True, **{notify_flag: True}):
        if settings_obj.channel_id:
            send_slack_message(settings_obj.channel_id, text, blocks=blocks)


def notify_slack_task_assigned(task):
    text = (
        f"New task assigned: {task.title}\n"
        f"Priority: {task.get_priority_display()}\n"
        f"Status: {task.get_status_display()}"
    )
    _notify_enabled_channels('notify_tasks', text)


def notify_slack_meeting(meeting):
    text = (
        f"New meeting scheduled: {meeting.title}\n"
        f"Time: {meeting.start_time} to {meeting.end_time}\n"
        f"Organizer: {meeting.organizer.get_full_name() or meeting.organizer.email}"
    )
    _notify_enabled_channels('notify_meetings', text)
