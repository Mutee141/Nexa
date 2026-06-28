from django.urls import path
from . import views

urlpatterns = [
    path('',                            views.billing_dashboard,       name='billing_dashboard'),
    path('pricing/',                    views.pricing_page,            name='pricing_page'),
    path('checkout/<str:plan>/',        views.create_checkout_session, name='create_checkout'),
    path('success/',                    views.checkout_success,        name='checkout_success'),
    path('cancel/',                     views.cancel_subscription,     name='cancel_subscription'),
    path('webhook/',                    views.stripe_webhook,          name='stripe_webhook'),
]