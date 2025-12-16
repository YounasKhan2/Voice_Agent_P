from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Session, Utterance, User, UserPreferences


class UtteranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utterance
        fields = ["id", "session", "role", "text", "event", "is_final", "created_at"]
        read_only_fields = ["id", "created_at"]


class SessionSerializer(serializers.ModelSerializer):
    utterances = UtteranceSerializer(many=True, read_only=True)

    class Meta:
        model = Session
        fields = ["id", "room", "user_id", "system_prompt", "started_at", "ended_at", "metadata", "utterances"]
        read_only_fields = ["id", "started_at", "utterances"]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile responses."""
    class Meta:
        model = User
        fields = ["id", "email", "display_name", "created_at"]
        read_only_fields = ["id", "created_at"]


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration with validation."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )
    
    class Meta:
        model = User
        fields = ["email", "password", "display_name"]
    
    def validate_email(self, value):
        """Validate email format and uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_password(self, value):
        """Validate password strength (minimum 8 characters)."""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        # Skip Django's strict password validators - let users choose their password
        return value
    
    def create(self, validated_data):
        """Create user with hashed password."""
        user = User.objects.create_user(
            username=validated_data['email'],  # Django requires username
            email=validated_data['email'],
            password=validated_data['password'],
            display_name=validated_data['display_name']
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for user preferences."""
    class Meta:
        model = UserPreferences
        fields = ["preferred_voice", "preferred_language", "favorite_topics", "system_prompt_override"]


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile with preferences."""
    preferences = UserPreferencesSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ["id", "email", "display_name", "created_at", "preferences"]
        read_only_fields = ["id", "created_at"]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = ["display_name", "email"]
    
    def validate_email(self, value):
        """Validate email uniqueness and format."""
        user = self.instance
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    current_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        min_length=8
    )
    
    def validate_new_password(self, value):
        """Validate new password strength."""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        # Skip Django's strict password validators - let users choose their password
        return value


class SessionHistoryListSerializer(serializers.ModelSerializer):
    """Serializer for session history list with utterance count."""
    utterance_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Session
        fields = ["id", "room", "started_at", "ended_at", "system_prompt", "utterance_count"]
        read_only_fields = ["id", "started_at", "ended_at"]
    
    def get_utterance_count(self, obj):
        """Return the count of utterances for this session."""
        return obj.utterances.count()


class SessionHistoryDetailSerializer(serializers.ModelSerializer):
    """Serializer for session detail with all utterances."""
    utterances = UtteranceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Session
        fields = ["id", "room", "started_at", "ended_at", "system_prompt", "metadata", "utterances"]
        read_only_fields = ["id", "started_at", "ended_at", "utterances"]
