from django.urls import path
from . import views

urlpatterns = [
    path('',        views.onboarding_wizard,  name='onboarding_wizard'),
    path('step1/',  views.onboarding_step1,   name='onboarding_step1'),
    path('step2/',  views.onboarding_step2,   name='onboarding_step2'),
    path('step3/',  views.onboarding_step3,   name='onboarding_step3'),
    path('step4/',  views.onboarding_step4,   name='onboarding_step4'),
    path('skip/',   views.skip_onboarding,    name='skip_onboarding'),
]