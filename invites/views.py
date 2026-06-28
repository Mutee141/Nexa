from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Invite
from accounts.models import User


@login_required
def invite_list(request):
    invites = Invite.objects.filter(invited_by=request.user).order_by('-created_at')
    return render(request, 'invites/invite_list.html', {'invites': invites})


@login_required
def send_invite(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        role  = request.POST.get('role', 'employee')

        if not email:
            messages.error(request, 'Email is required.')
            return redirect('invite_list')

        if User.objects.filter(email=email).exists():
            messages.error(request, f'{email} already has an account.')
            return redirect('invite_list')

        if Invite.objects.filter(email=email, is_used=False).exists():
            messages.error(request, f'An invite was already sent to {email}.')
            return redirect('invite_list')

        invite = Invite.objects.create(
            email=email,
            role=role,
            invited_by=request.user,
        )

        invite_url = f"{settings.SITE_URL}/invites/accept/{invite.token}/"

        try:
            send_mail(
                subject='You are invited to NexaOps',
                message=(
                    f"Hi!\n\n"
                    f"{request.user.get_full_name() or request.user.email} invited you to join NexaOps.\n\n"
                    f"Click this link to create your account:\n{invite_url}\n\n"
                    f"This link expires in 7 days.\n\n"
                    f"NexaOps Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, f'Invite sent to {email}!')
        return redirect('invite_list')

    return redirect('invite_list')


def accept_invite(request, token):
    invite = get_object_or_404(Invite, token=token, is_used=False)

    if invite.is_expired():
        messages.error(request, 'This invite link has expired.')
        return redirect('account_login')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name  = request.POST.get('last_name', '')
        password   = request.POST.get('password', '')
        confirm    = request.POST.get('confirm_password', '')

        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'invites/accept.html', {'invite': invite})

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'invites/accept.html', {'invite': invite})

        if User.objects.filter(email=invite.email).exists():
            messages.error(request, 'An account with this email already exists.')
            return redirect('account_login')

        username = invite.email.split('@')[0]
        base = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=invite.email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )

        invite.is_used = True
        invite.save()

        messages.success(request, f'Welcome {first_name}! Your account has been created. Please sign in.')
        return redirect('account_login')

    return render(request, 'invites/accept.html', {'invite': invite})


@login_required
def revoke_invite(request, pk):
    invite = get_object_or_404(Invite, pk=pk, invited_by=request.user)
    if request.method == 'POST':
        invite.delete()
        messages.success(request, 'Invite revoked.')
    return redirect('invite_list')