from django.shortcuts import render
from django.shortcuts import render
from accounts.decorators import admin_required
from .models import AuditLog
from accounts.models import User


@admin_required
def audit_log_list(request):
    logs = AuditLog.objects.select_related('user').all()

    action_filter = request.GET.get('action')
    user_filter   = request.GET.get('user')
    model_filter  = request.GET.get('model')

    if action_filter:
        logs = logs.filter(action=action_filter)
    if user_filter:
        logs = logs.filter(user_id=user_filter)
    if model_filter:
        logs = logs.filter(model_name=model_filter)

    context = {
        'logs':       logs[:200],
        'total':      AuditLog.objects.count(),
        'users':      User.objects.all(),
        'models':     AuditLog.objects.values_list('model_name', flat=True).distinct(),
        'selected_action': action_filter or '',
        'selected_user':   user_filter or '',
        'selected_model':  model_filter or '',
    }
    return render(request, 'audit/audit_log.html', context)


@admin_required
def export_audit_csv(request):
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="nexaops_audit_log.csv"'

    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'User', 'Action', 'Model', 'Object', 'IP Address'])

    logs = AuditLog.objects.select_related('user').all()
    for log in logs:
        writer.writerow([
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            log.user.email if log.user else 'System',
            log.get_action_display(),
            log.model_name,
            log.object_repr,
            log.ip_address or '',
        ])

    return response