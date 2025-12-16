from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    """Health check endpoint for Azure App Service"""
    return JsonResponse({"status": "healthy", "service": "django-persistence"})

urlpatterns = [
    path('health/', health_check, name='health'),
    path('admin/', admin.site.urls),
    path('api/', include('conversation.urls')),
]
