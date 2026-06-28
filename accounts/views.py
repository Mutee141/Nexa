from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .models import User


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


@login_required
def profile_edit(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name  = request.POST.get('last_name', '')
        user.job_title  = request.POST.get('job_title', '')
        user.phone      = request.POST.get('phone', '')
        user.bio        = request.POST.get('bio', '')

        # Handle avatar upload
        if request.FILES.get('avatar'):
            user.avatar = request.FILES['avatar']

        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'accounts/profile_edit.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        current  = request.POST.get('current_password')
        new_pass = request.POST.get('new_password')
        confirm  = request.POST.get('confirm_password')

        if not request.user.check_password(current):
            messages.error(request, 'Current password is incorrect.')
            return redirect('change_password')

        if new_pass != confirm:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')

        if len(new_pass) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return redirect('change_password')

        request.user.set_password(new_pass)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, 'Password changed successfully!')
        return redirect('profile')

    return render(request, 'accounts/change_password.html')



@login_required
def api_settings(request):
    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=request.user)
    return render(request, 'accounts/api_settings.html', {'token': token})


@login_required
def regenerate_token(request):
    from rest_framework.authtoken.models import Token
    if request.method == 'POST':
        Token.objects.filter(user=request.user).delete()
        Token.objects.create(user=request.user)
        messages.success(request, 'API token regenerated!')
    return redirect('api_settings')