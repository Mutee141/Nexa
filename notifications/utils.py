from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, NotificationPreference


def get_or_create_preferences(user):
    prefs, _ = NotificationPreference.objects.get_or_create(user=user)
    return prefs


def send_notification(recipient, sender, notif_type, title, message, link='', send_email=False, email_subject=None):
    """
    Main function to create a notification.
    Call this from anywhere in the project.
    """
    # Check user preferences
    prefs = get_or_create_preferences(recipient)

    # Map notif_type to preference field
    pref_map = {
        'task_assigned':    'task_assigned',
        'task_due':         'task_due',
        'task_completed':   'task_completed',
        'project_update':   'project_update',
        'meeting_reminder': 'meeting_reminder',
        'meeting_created':  'meeting_created',
        'document_upload':  'document_upload',
        'general':          None,
    }

    pref_field = pref_map.get(notif_type)
    if pref_field and not getattr(prefs, pref_field, True):
        return None  # User turned this off

    # Create in-app notification
    notif = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notif_type=notif_type,
        title=title,
        message=message,
        link=link,
    )

    # Send email if requested and user allows it
    if send_email:
        email_pref_map = {
            'task_assigned':    'email_task_assigned',
            'task_due':         'email_task_due',
            'meeting_reminder': 'email_meeting_reminder',
            'meeting_created':  'email_meeting_created',
        }
        email_pref = email_pref_map.get(notif_type)
        should_email = getattr(prefs, email_pref, False) if email_pref else False

        if should_email:
            try:
                send_mail(
                    subject=email_subject or title,
                    message=f"{message}\n\nView it here: {settings.SITE_URL}{link}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=True,
                )
            except Exception:
                pass  # Never crash the app because of email

    return notif


# ---- Shortcut helper functions ----

def notify_task_assigned(task, assigned_by):
    if not task.assigned_to:
        return
    send_notification(
        recipient=task.assigned_to,
        sender=assigned_by,
        notif_type='task_assigned',
        title=f'New task assigned: {task.title}',
        message=f'{assigned_by.get_full_name() or assigned_by.email} assigned you a task: "{task.title}". Priority: {task.get_priority_display()}.',
        link=f'/tasks/{task.pk}/',
        send_email=True,
        email_subject=f'[NexaOps] Task assigned: {task.title}',
    )


def notify_task_completed(task):
    if not task.assigned_to:
        return
    send_notification(
        recipient=task.created_by,
        sender=task.assigned_to,
        notif_type='task_completed',
        title=f'Task completed: {task.title}',
        message=f'{task.assigned_to.get_full_name() or task.assigned_to.email} completed the task "{task.title}".',
        link=f'/tasks/{task.pk}/',
    )


def notify_meeting_created(meeting):
    for attendee in meeting.attendees.all():
        if attendee == meeting.organizer:
            continue
        send_notification(
            recipient=attendee,
            sender=meeting.organizer,
            notif_type='meeting_created',
            title=f'Meeting scheduled: {meeting.title}',
            message=f'{meeting.organizer.get_full_name() or meeting.organizer.email} scheduled a meeting: "{meeting.title}" on {meeting.start_time.strftime("%B %d at %I:%M %p")}.',
            link=f'/meetings/{meeting.pk}/',
            send_email=True,
            email_subject=f'[NexaOps] Meeting: {meeting.title}',
        )


def notify_project_update(project, updater, action='updated'):
    for member in project.members.all():
        if member == updater:
            continue
        send_notification(
            recipient=member,
            sender=updater,
            notif_type='project_update',
            title=f'Project {action}: {project.name}',
            message=f'{updater.get_full_name() or updater.email} {action} the project "{project.name}".',
            link=f'/projects/{project.pk}/',
        )


def notify_document_upload(document):
    from accounts.models import User
    for user in User.objects.exclude(pk=document.uploaded_by.pk):
        send_notification(
            recipient=user,
            sender=document.uploaded_by,
            notif_type='document_upload',
            title=f'New document: {document.title}',
            message=f'{document.uploaded_by.get_full_name() or document.uploaded_by.email} uploaded "{document.title}" in {document.get_category_display()}.',
            link='/documents/',
        )