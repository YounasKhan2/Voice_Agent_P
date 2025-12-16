from typing import List
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Session, Utterance, User, UserPreferences
from .serializers import (
    SessionSerializer, 
    UtteranceSerializer, 
    UserSerializer, 
    RegisterSerializer, 
    LoginSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserPreferencesSerializer,
    PasswordChangeSerializer,
    SessionHistoryListSerializer,
    SessionHistoryDetailSerializer
)


class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Session.objects.all().order_by("-started_at")
    serializer_class = SessionSerializer


class UtteranceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Utterance.objects.select_related("session").all().order_by("-created_at")
    serializer_class = UtteranceSerializer


class IngestView(APIView):
    """
    POST /api/ingest
    Body: {
      "session": { "id": "uuid", "room": "name", "user_id": "...", "system_prompt": "..." },
      "events": [ { "role": "user|agent|event", "text": "...", "event": "speech_started|...", "is_final": true } ]
    }
    Security: header X-INGEST-TOKEN must match settings.ALLOW_INGEST_TOKEN
    """
    # Use header token for auth instead of DRF's default IsAuthenticatedOrReadOnly
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        token = request.headers.get("X-INGEST-TOKEN")
        if not token or token != getattr(settings, "ALLOW_INGEST_TOKEN", ""):
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        payload = request.data or {}
        sess = payload.get("session") or {}
        events: List[dict] = payload.get("events") or []

        if not sess:
            return Response({"detail": "Missing session"}, status=status.HTTP_400_BAD_REQUEST)

        session_id = sess.get("id")
        if not session_id:
            return Response({"detail": "Missing session id"}, status=status.HTTP_400_BAD_REQUEST)

        session, _ = Session.objects.get_or_create(
            id=session_id,
            defaults={
                "room": sess.get("room", "unknown"),
                "user_id": sess.get("user_id"),
                "system_prompt": sess.get("system_prompt", ""),
                "metadata": sess.get("metadata"),
            },
        )

        created = []
        for e in events:
            role = e.get("role")
            text = e.get("text", "")
            event = e.get("event", "")
            is_final = bool(e.get("is_final", True))
            created.append(
                Utterance(session=session, role=role or "event", text=text, event=event, is_final=is_final)
            )

        if created:
            Utterance.objects.bulk_create(created)
        # Update end time if provided
        if sess.get("ended_at") and not session.ended_at:
            session.ended_at = timezone.now()
            session.save(update_fields=["ended_at"])

        return Response({"created": len(created)}, status=status.HTTP_200_OK)


# Authentication Endpoints

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def register_view(request):
    """
    POST /api/auth/register
    Register a new user and create session.
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Create UserPreferences record
        UserPreferences.objects.create(user=user)
        
        # Create Django session and set session cookie
        login(request, user)
        
        # Return user data (excluding password hash)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def login_view(request):
    """
    POST /api/auth/login
    Authenticate user and create session.
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    # Authenticate user credentials
    user = authenticate(request, username=email, password=password)
    
    if user is not None:
        # Create Django session on successful authentication
        login(request, user)
        
        # Return user data on success
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
    
    # Return error on failure (don't reveal whether email exists)
    return Response(
        {"detail": "Invalid credentials"},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def logout_view(request):
    """
    POST /api/auth/logout
    Destroy server-side session and clear session cookie.
    """
    # Logout even if user is not authenticated (idempotent operation)
    if request.user.is_authenticated:
        logout(request)
    return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def me_view(request):
    """
    GET /api/auth/me
    Get current authenticated user data.
    Returns 401 if not authenticated.
    """
    if request.user.is_authenticated:
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
    
    return Response({"authenticated": False}, status=status.HTTP_401_UNAUTHORIZED)


# User Profile and Preferences Endpoints

@csrf_exempt
@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    """
    GET /api/users/profile
    Retrieve authenticated user's profile with preferences.
    
    PATCH /api/users/profile
    Update authenticated user's profile (display_name, email).
    
    Requires authentication via session cookie.
    Returns 401 if not authenticated.
    """
    # Ensure UserPreferences exists for the user
    UserPreferences.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Return updated profile with preferences
            profile_serializer = UserProfileSerializer(request.user)
            return Response(profile_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
@csrf_exempt
def preferences_view(request):
    """
    PUT /api/users/preferences
    Update authenticated user's preferences.
    Accepts preferred_voice, preferred_language, favorite_topics.
    Creates UserPreferences if doesn't exist.
    Requires authentication via session cookie.
    Returns 401 if not authenticated.
    """
    # Get or create UserPreferences for the user
    preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    serializer = UserPreferencesSerializer(preferences, data=request.data, partial=False)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@csrf_exempt
def change_password_view(request):
    """
    POST /api/users/change-password
    Change authenticated user's password.
    Requires current password validation.
    Hashes and stores new password.
    Requires authentication via session cookie.
    Returns 401 if not authenticated.
    """
    serializer = PasswordChangeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    current_password = serializer.validated_data['current_password']
    new_password = serializer.validated_data['new_password']
    
    # Validate current password
    if not request.user.check_password(current_password):
        return Response(
            {"current_password": ["Current password is incorrect."]},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Hash and store new password
    request.user.set_password(new_password)
    request.user.save()
    
    return Response(
        {"message": "Password changed successfully"},
        status=status.HTTP_200_OK
    )


# Conversation History Endpoints

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def history_list_view(request):
    """
    GET /api/users/history
    Retrieve authenticated user's conversation history.
    Query sessions filtered by user foreign key.
    Order by started_at descending.
    Include pagination (limit, offset).
    Return session metadata with utterance count.
    
    Query params:
    - limit: Number of results to return (default: 20)
    - offset: Number of results to skip (default: 0)
    
    Requires authentication via session cookie.
    Returns 401 if not authenticated.
    """
    # Get pagination parameters
    try:
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        return Response(
            {"detail": "Invalid pagination parameters"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Ensure limit is reasonable
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 20
    if offset < 0:
        offset = 0
    
    # Query sessions filtered by user foreign key, ordered by started_at descending
    sessions = Session.objects.filter(
        user_account=request.user
    ).order_by('-started_at').prefetch_related('utterances')
    
    # Get total count
    total_count = sessions.count()
    
    # Apply pagination
    paginated_sessions = sessions[offset:offset + limit]
    
    # Serialize the results
    serializer = SessionHistoryListSerializer(paginated_sessions, many=True)
    
    # Build pagination response
    next_url = None
    previous_url = None
    
    if offset + limit < total_count:
        next_url = f"/api/users/history?limit={limit}&offset={offset + limit}"
    
    if offset > 0:
        previous_offset = max(0, offset - limit)
        previous_url = f"/api/users/history?limit={limit}&offset={previous_offset}"
    
    return Response({
        "count": total_count,
        "next": next_url,
        "previous": previous_url,
        "results": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def history_detail_view(request, session_id):
    """
    GET /api/users/history/{session_id}
    Retrieve a specific session's details with all utterances.
    Verify session belongs to authenticated user.
    Return session metadata and all utterances.
    Return 404 if session not found or doesn't belong to user.
    Order utterances by created_at.
    
    Requires authentication via session cookie.
    Returns 401 if not authenticated.
    """
    try:
        # Query session and verify it belongs to authenticated user
        session = Session.objects.prefetch_related('utterances').get(
            id=session_id,
            user_account=request.user
        )
    except Session.DoesNotExist:
        return Response(
            {"detail": "Session not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Serialize the session with all utterances (ordered by created_at via model Meta)
    serializer = SessionHistoryDetailSerializer(session)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


# Internal Endpoints (for FastAPI backend)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def validate_session_view(request):
    """
    POST /api/internal/validate-session
    Internal endpoint for FastAPI to validate session cookies.
    
    Accept session cookie in request.
    Check if user is authenticated.
    Return user_id, email, display_name, and preferences if valid.
    Return 401 if session invalid.
    
    Do not expose this endpoint publicly (internal use only).
    
    This endpoint is called by the FastAPI backend to validate user sessions
    and retrieve user preferences for authenticated voice conversations.
    """
    if request.user.is_authenticated:
        # Get user preferences (create if doesn't exist)
        preferences, created = UserPreferences.objects.get_or_create(user=request.user)
        
        # Build preferences dict
        preferences_data = {
            'preferred_voice': preferences.preferred_voice,
            'preferred_language': preferences.preferred_language,
            'favorite_topics': preferences.favorite_topics,
            'system_prompt_override': preferences.system_prompt_override,
        }
        
        return Response({
            'valid': True,
            'user_id': str(request.user.id),
            'email': request.user.email,
            'display_name': request.user.display_name,
            'preferences': preferences_data
        }, status=status.HTTP_200_OK)
    
    return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def save_session_view(request):
    """
    POST /api/users/sessions/save
    Save current voice session to user's history.
    
    Request body:
    {
      "session_id": "uuid",
      "messages": [
        {"role": "user", "text": "...", "timestamp": 1234567890},
        {"role": "agent", "text": "...", "timestamp": 1234567891}
      ]
    }
    
    - Verify session_id exists
    - Associate session with authenticated user
    - Mark session as ended
    - Create missing utterances from messages array
    - Return saved session metadata
    """
    session_id = request.data.get('session_id')
    messages = request.data.get('messages', [])
    
    if not session_id:
        return Response(
            {"detail": "session_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get session and verify it's not already associated with another user
        session = Session.objects.get(id=session_id)
        
        # Associate with current user if not already set
        if not session.user_account:
            session.user_account = request.user
            session.ended_at = timezone.now()
            session.save()
        elif session.user_account != request.user:
            return Response(
                {"detail": "Session belongs to another user"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create final utterances from message sequence if needed
        # (This ensures we have the complete conversation even if
        # some messages weren't captured via the ingest endpoint)
        existing_utterances = set(
            session.utterances.filter(is_final=True)
            .values_list('text', 'role')
        )
        
        new_utterances = []
        for msg in messages:
            msg_tuple = (msg.get('text'), msg.get('role'))
            if msg_tuple not in existing_utterances:
                new_utterances.append(
                    Utterance(
                        session=session,
                        role=msg.get('role', 'user'),
                        text=msg.get('text', ''),
                        is_final=True,
                        created_at=timezone.datetime.fromtimestamp(
                            msg.get('timestamp', 0) / 1000,
                            tz=timezone.utc
                        ) if msg.get('timestamp') else timezone.now()
                    )
                )
        
        if new_utterances:
            Utterance.objects.bulk_create(new_utterances)
        
        # Return session metadata
        serializer = SessionHistoryListSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Session.DoesNotExist:
        return Response(
            {"detail": "Session not found"},
            status=status.HTTP_404_NOT_FOUND
        )
