from django.shortcuts import redirect
from django.urls import reverse


class OnboardingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            exempt_paths = ['/onboarding/', '/accounts/logout/', '/static/', '/media/']
            if not any(request.path.startswith(p) for p in exempt_paths):
                if not request.user.has_completed_onboarding:
                    return redirect('/onboarding/')
        return self.get_response(request)