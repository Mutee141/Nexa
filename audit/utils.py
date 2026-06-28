from .models import AuditLog


def log_action(request, action, model_name, object_repr, object_id='', extra_info=''):
    """Call this from any view to log an action"""
    try:
        ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() \
             or request.META.get('REMOTE_ADDR', '')

        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action=action,
            model_name=model_name,
            object_repr=str(object_repr)[:255],
            object_id=str(object_id),
            ip_address=ip or None,
            extra_info=extra_info,
        )
    except Exception:
        pass  # Never break the app because of logging