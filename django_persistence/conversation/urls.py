from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SessionViewSet, 
    UtteranceViewSet, 
    IngestView,
    register_view,
    login_view,
    logout_view,
    me_view,
    profile_view,
    preferences_view,
    change_password_view,
    history_list_view,
    history_detail_view,
    validate_session_view,
    save_session_view
)

router = DefaultRouter()
router.register(r'sessions', SessionViewSet, basename='session')
router.register(r'utterances', UtteranceViewSet, basename='utterance')

urlpatterns = [
    path('', include(router.urls)),
    path('ingest', IngestView.as_view()),
    # Authentication endpoints
    path('auth/register', register_view, name='auth-register'),
    path('auth/login', login_view, name='auth-login'),
    path('auth/logout', logout_view, name='auth-logout'),
    path('auth/me', me_view, name='auth-me'),
    # User profile and preferences endpoints
    path('users/profile', profile_view, name='user-profile'),
    path('users/preferences', preferences_view, name='user-preferences'),
    path('users/change-password', change_password_view, name='change-password'),
    # Conversation history endpoints
    path('users/history', history_list_view, name='history-list'),
    path('users/history/<uuid:session_id>', history_detail_view, name='history-detail'),
    path('users/sessions/save', save_session_view, name='save-session'),
    # Internal endpoints (for FastAPI backend)
    path('internal/validate-session', validate_session_view, name='validate-session'),
]
