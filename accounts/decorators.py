from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from functools import wraps


def admin_required(view_func):
    """Only Admin role or superuser can access"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin_role():
            messages.error(request, 'You need Admin access for this page.')
            return redirect('dashboard_home')
        return view_func(request, *args, **kwargs)
    return wrapper


def manager_required(view_func):
    """Admin or Manager role can access"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_manager_role():
            messages.error(request, 'You need Manager access for this page.')
            return redirect('dashboard_home')
        return view_func(request, *args, **kwargs)
    return wrapper