#!/usr/bin/env python3
"""
Reset Users Script
Deletes all users, sessions, and related data from the database
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from conversation.models import User, Session, Utterance, UserPreferences

def reset_database():
    print("=" * 60)
    print("RESETTING DATABASE")
    print("=" * 60)
    
    # Count before deletion
    user_count = User.objects.count()
    session_count = Session.objects.count()
    utterance_count = Utterance.objects.count()
    prefs_count = UserPreferences.objects.count()
    
    print(f"\nBefore deletion:")
    print(f"  Users: {user_count}")
    print(f"  Sessions: {session_count}")
    print(f"  Utterances: {utterance_count}")
    print(f"  Preferences: {prefs_count}")
    
    # Delete all data
    print("\nDeleting all data...")
    
    # Delete utterances first (foreign key to sessions)
    deleted_utterances = Utterance.objects.all().delete()
    print(f"  ✓ Deleted {deleted_utterances[0]} utterances")
    
    # Delete sessions (foreign key to users)
    deleted_sessions = Session.objects.all().delete()
    print(f"  ✓ Deleted {deleted_sessions[0]} sessions")
    
    # Delete preferences (one-to-one with users)
    deleted_prefs = UserPreferences.objects.all().delete()
    print(f"  ✓ Deleted {deleted_prefs[0]} preferences")
    
    # Delete users
    deleted_users = User.objects.all().delete()
    print(f"  ✓ Deleted {deleted_users[0]} users")
    
    # Verify deletion
    print("\nAfter deletion:")
    print(f"  Users: {User.objects.count()}")
    print(f"  Sessions: {Session.objects.count()}")
    print(f"  Utterances: {Utterance.objects.count()}")
    print(f"  Preferences: {UserPreferences.objects.count()}")
    
    print("\n" + "=" * 60)
    print("✓ DATABASE RESET COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    reset_database()
