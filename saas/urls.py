from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/',   include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('tasks/',     include('tasks.urls')),
    path('projects/',  include('projects.urls')),
    path('employees/', include('employees.urls')),
    path('meetings/',  include('meetings.urls')),
    path('documents/', include('documents.urls')),
    path('ai/',         include('ai.urls')),
    
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)