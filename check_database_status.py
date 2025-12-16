#!/usr/bin/env python3
"""
Check Database Status
Shows current state of users, sessions, and messages
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import sys
sys.path.insert(0, 'django_persistence')
django.setup()

from conversation.models import User, Session, Utterance, UserPreferences

def check_database():
    print("=" * 60)
    print("DATABASE STATUS CHECK")
    print("=" * 60)
    
    # Check users
    users = User.objects.all()
    print(f"\n👥 USERS: {users.count()}")
    for user in users:
        print(f"  - {user.email} ({user.display_name})")
    
    # Check sessions
    sessions = Session.objects.all().order_by('-started_at')
    print(f"\n💬 SESSIONS: {sessions.count()}")
    for session in sessions[:5]:  # Show last 5
        user_name = session.user_account.display_name if session.user_account else "Anonymous"
        msg_count = session.utterances.count()
        print(f"  - {session.id} | User: {user_name} | Messages: {msg_count} | Started: {session.started_at}")
    
    # Check messages
    utterances = Utterance.objects.all()
    print(f"\n💭 MESSAGES: {utterances.count()}")
    
    # Check recent messages
    recent = Utterance.objects.filter(is_final=True).order_by('-created_at')[:10]
    print(f"\n📝 RECENT MESSAGES (last 10):")
    for utt in recent:
        text_preview = utt.text[:50] + "..." if len(utt.text) > 50 else utt.text
        print(f"  [{utt.role}] {text_preview}")
    
    # Check for the specific user
    print(f"\n🔍 CHECKING USER: younaskk120@gmail.com")
    try:
        user = User.objects.get(email='younaskk120@gmail.com')
        user_sessions = Session.objects.filter(user_account=user)
        print(f"  - User ID: {user.id}")
        print(f"  - Display Name: {user.display_name}")
        print(f"  - Sessions: {user_sessions.count()}")
        print(f"  - Has Preferences: {hasattr(user, 'preferences')}")
        
        if user_sessions.exists():
            print(f"\n  User's Sessions:")
            for sess in user_sessions:
                print(f"    - {sess.id} | Messages: {sess.utterances.count()} | {sess.started_at}")
        else:
            print(f"  ⚠️  No sessions found for this user")
            
    except User.DoesNotExist:
        print(f"  ❌ User not found!")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_database()
