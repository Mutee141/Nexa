from django.urls import path
from . import views

urlpatterns = [
    path('',        views.home,    name='landing_home'),
    path('about/',  views.about,   name='landing_about'),
    path('contact/',views.contact, name='landing_contact'),
]