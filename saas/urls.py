from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="NexaOps API",
        default_version='v1',
        description="AI-powered business operations platform API",
        contact=openapi.Contact(email="api@nexaops.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('accounts/',   include('allauth.urls')),
    path('accounts/',   include('accounts.urls')),
    path('dashboard/',  include('dashboard.urls')),
    path('tasks/',      include('tasks.urls')),
    path('projects/',   include('projects.urls')),
    path('employees/',  include('employees.urls')),
    path('meetings/',   include('meetings.urls')),
    path('documents/',  include('documents.urls')),
    path('ai/',         include('ai.urls')),
    path('notifications/', include('notifications.urls')),
    path('analytics/',  include('analytics.urls')),
    path('billing/',    include('billing.urls')),
    path('timetracking/', include('timetracking.urls')),
    path('invites/',    include('invites.urls')),
    path('audit/',      include('audit.urls')),
    path('onboarding/', include('onboarding.urls')),
    path('slack/', include('slack_integration.urls')),

    
    path('api/v1/',     include('api.urls')),
    path('api/token/',  obtain_auth_token, name='api_token_auth'),
    path('api/docs/',   schema_view.with_ui('swagger', cache_timeout=0), name='api_docs'),

    path('', include('landing.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)