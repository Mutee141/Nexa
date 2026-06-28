from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.document_list,      name='document_list'),
    path('upload/',             views.document_upload,    name='document_upload'),
    path('<int:pk>/edit/',      views.document_edit,      name='document_edit'),
    path('<int:pk>/delete/',    views.document_delete,    name='document_delete'),
    path('<int:pk>/summarize/', views.document_summarize, name='document_summarize'),
]