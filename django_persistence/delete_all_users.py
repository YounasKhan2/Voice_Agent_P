import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from conversation.models import User

# Get count before deletion
user_count = User.objects.count()
print(f"Found {user_count} users in the database")

if user_count > 0:
    # List all users
    print("\nUsers to be deleted:")
    for user in User.objects.all():
        print(f"  - {user.email} ({user.display_name})")
    
    # Delete all users
    User.objects.all().delete()
    print(f"\n✓ Successfully deleted all {user_count} users")
else:
    print("No users found in the database")

# Verify deletion
remaining = User.objects.count()
print(f"\nRemaining users: {remaining}")
