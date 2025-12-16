from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserPreferences, Session, Utterance


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin configuration for User model."""
    list_display = ['email', 'display_name', 'created_at', 'is_active']
    list_filter = ['is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'display_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('email', 'display_name', 'username', 'password')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_login')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'display_name', 'password1', 'password2'),
        }),
    )


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """Custom admin configuration for UserPreferences model."""
    list_display = ['user', 'preferred_voice', 'preferred_language', 'created_at']
    search_fields = ['user__email', 'user__display_name']
    list_filter = ['preferred_voice', 'preferred_language']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Preferences', {
            'fields': ('preferred_voice', 'preferred_language', 'favorite_topics', 'system_prompt_override')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "user_id", "started_at", "ended_at")
    search_fields = ("id", "room", "user_id")
    readonly_fields = ("started_at",)


@admin.register(Utterance)
class UtteranceAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "role", "is_final", "created_at", "event")
    search_fields = ("session__id", "text")
    readonly_fields = ("created_at",)
