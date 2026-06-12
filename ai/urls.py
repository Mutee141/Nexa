from django.urls import path
from . import views

urlpatterns = [
    path('assistant/',      views.assistant,      name='ai_assistant'),
    path('chat/',           views.chat,            name='ai_chat'),
    path('email-writer/',   views.email_writer,    name='ai_email_writer'),
    path('task-generator/', views.task_generator,  name='ai_task_generator'),
    path('summarize/<int:doc_id>/', views.summarize_doc, name='ai_summarize_doc'),
]