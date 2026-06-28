from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification, NotificationPreference
from .utils import get_or_create_preferences


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender')

    # Mark all as read when page is opened
    notifications.filter(is_read=False).update(is_read=True)

    context = {
        'notifications': notifications[:50],
        'total': notifications.count(),
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
def notification_count(request):
    """API endpoint — returns unread count for the bell icon"""
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    return JsonResponse({'count': count})


@login_required
def notification_dropdown(request):
    """API endpoint — returns last 8 notifications as HTML"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender')[:8]

    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()

    return render(request, 'notifications/dropdown.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
@require_POST
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
def clear_all(request):
    Notification.objects.filter(recipient=request.user).delete()
    return JsonResponse({'status': 'ok'})


@login_required
def notification_preferences(request):
    prefs = get_or_create_preferences(request.user)

    if request.method == 'POST':
        # In-app preferences
        prefs.task_assigned     = 'task_assigned'     in request.POST
        prefs.task_due          = 'task_due'           in request.POST
        prefs.task_completed    = 'task_completed'     in request.POST
        prefs.project_update    = 'project_update'     in request.POST
        prefs.meeting_reminder  = 'meeting_reminder'   in request.POST
        prefs.meeting_created   = 'meeting_created'    in request.POST
        prefs.document_upload   = 'document_upload'    in request.POST
        # Email preferences
        prefs.email_task_assigned    = 'email_task_assigned'    in request.POST
        prefs.email_task_due         = 'email_task_due'          in request.POST
        prefs.email_meeting_reminder = 'email_meeting_reminder'  in request.POST
        prefs.email_meeting_created  = 'email_meeting_created'   in request.POST
        prefs.save()

        from django.contrib import messages
        messages.success(request, 'Notification preferences saved!')
        return redirect('notification_preferences')

    return render(request, 'notifications/preferences.html', {'prefs': prefs})