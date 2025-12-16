#!/usr/bin/env python3
"""
Create Users Script
Creates Django superuser and regular user
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from conversation.models import User, UserPreferences

def create_users():
    print("=" * 60)
    print("CREATING USERS")
    print("=" * 60)
    
    # Create Django superuser
    print("\n1. Creating Django superuser...")
    try:
        superuser = User.objects.create_superuser(
            email='younaskk120@gmail.com',
            password='12345678',
            display_name='Admin User'
        )
        print(f"   ✓ Superuser created: {superuser.email}")
        print(f"   - Display Name: {superuser.display_name}")
        print(f"   - Is Staff: {superuser.is_staff}")
        print(f"   - Is Superuser: {superuser.is_superuser}")
        
        # Create preferences for superuser
        prefs = UserPreferences.objects.create(
            user=superuser,
            preferred_voice='alloy',
            preferred_language='en'
        )
        print(f"   ✓ Preferences created for superuser")
        
    except Exception as e:
        print(f"   ✗ Error creating superuser: {e}")
    
    # Create regular user (same credentials for Flask frontend)
    print("\n2. Creating regular user for Flask frontend...")
    try:
        # Check if user already exists (superuser might have same email)
        if User.objects.filter(email='younaskk120@gmail.com').exists():
            user = User.objects.get(email='younaskk120@gmail.com')
            print(f"   ℹ User already exists: {user.email}")
            print(f"   - Using existing user for Flask frontend")
        else:
            user = User.objects.create_user(
                email='younaskk120@gmail.com',
                password='12345678',
                display_name='Younas Khan'
            )
            print(f"   ✓ User created: {user.email}")
            print(f"   - Display Name: {user.display_name}")
            
            # Create preferences for user
            prefs = UserPreferences.objects.create(
                user=user,
                preferred_voice='alloy',
                preferred_language='en'
            )
            print(f"   ✓ Preferences created for user")
        
    except Exception as e:
        print(f"   ✗ Error creating user: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Users: {User.objects.count()}")
    print(f"Total Superusers: {User.objects.filter(is_superuser=True).count()}")
    print(f"Total Preferences: {UserPreferences.objects.count()}")
    
    print("\n📋 LOGIN CREDENTIALS:")
    print("-" * 60)
    print("Email:    younaskk120@gmail.com")
    print("Password: 12345678")
    print("-" * 60)
    print("\n✓ Django Admin: http://127.0.0.1:9000/admin/")
    print("✓ Flask Login:  http://127.0.0.1:5173/login")
    
    print("\n" + "=" * 60)
    print("✓ USERS CREATED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    create_users()
