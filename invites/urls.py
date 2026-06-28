from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.invite_list,   name='invite_list'),
    path('send/',                   views.send_invite,   name='send_invite'),
    path('accept/<uuid:token>/',    views.accept_invite, name='accept_invite'),
    path('<int:pk>/revoke/',        views.revoke_invite, name='revoke_invite'),
]