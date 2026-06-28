from django.urls import path
from . import views

urlpatterns = [
    path('assistant/',      views.assistant,      name='ai_assistant'),
    path('chat/',           views.chat,            name='ai_chat'),
    path('email-writer/',   views.email_writer,    name='ai_email_writer'),
    path('task-generator/', views.task_generator,  name='ai_task_generator'),
    path('summarize/<int:doc_id>/', views.summarize_doc, name='ai_summarize_doc'),
    path('standup/', views.daily_standup, name='ai_standup'),
    path('search/', views.smart_search, name='ai_search'),
    path('performance-review/<int:employee_id>/', views.performance_review, name='ai_performance_review'),
    path('risk-detector/', views.risk_detector, name='ai_risk_detector'),
    path('agenda-builder/', views.agenda_builder, name='ai_agenda_builder'),
    path('proposal-writer/', views.proposal_writer, name='ai_proposal_writer'),

]