import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    """Custom user manager that uses email instead of username."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        # Set username to email if not provided
        extra_fields.setdefault('username', email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Uses email as the primary identifier.
    """
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Override groups and user_permissions to avoid clashes with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='conversation_user_set',
        related_query_name='conversation_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='conversation_user_set',
        related_query_name='conversation_user',
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['display_name']
    
    objects = UserManager()
    
    class Meta:
        db_table = 'conversation_user'
        indexes = [
            models.Index(fields=['email']),
        ]
    
    def __str__(self) -> str:
        return f"{self.display_name} ({self.email})"


class UserPreferences(models.Model):
    """
    Stores user-specific preferences for voice agent behavior.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    preferred_voice = models.CharField(max_length=50, default='alloy')
    preferred_language = models.CharField(max_length=10, default='en')
    favorite_topics = models.JSONField(default=list, blank=True)
    system_prompt_override = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_preferences'
    
    def __str__(self) -> str:
        return f"Preferences for {self.user.display_name}"


class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.CharField(max_length=128)
    user_id = models.CharField(max_length=128, blank=True, null=True)
    user_account = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    system_prompt = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user_account', '-started_at']),
        ]

    def __str__(self) -> str:
        return f"Session({self.id}) room={self.room} user={self.user_id}"


class Utterance(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("agent", "Agent"),
        ("event", "Event"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="utterances")
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    text = models.TextField(blank=True)
    event = models.CharField(max_length=64, blank=True)
    is_final = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Utterance({self.role}, final={self.is_final})"
