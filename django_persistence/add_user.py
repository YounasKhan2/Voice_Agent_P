import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from conversation.models import User

# Create or update user
email = 'younaskk120@gmail.com'
username = 'younaskk120'
password = '12345678'
display_name = 'Younas KK'

try:
    # Try to get existing user
    user = User.objects.get(email=email)
    print(f"User {email} already exists. Updating password...")
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"✓ Updated user: {email}")
except User.DoesNotExist:
    # Create new user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        display_name=display_name
    )
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"✓ Created superuser: {email}")

print(f"Email: {email}")
print(f"Password: {password}")
print(f"Display Name: {display_name}")
print(f"Is Superuser: {user.is_superuser}")
print(f"Is Staff: {user.is_staff}")
