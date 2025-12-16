import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from conversation.models import User

# Create superuser
email = "younaskk120@gmail.com"
password = "12345678"
display_name = "Admin User"

# Check if user already exists
if User.objects.filter(email=email).exists():
    print(f"User with email {email} already exists!")
    user = User.objects.get(email=email)
    print(f"Updating password for existing user...")
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"✅ Superuser updated successfully!")
else:
    # Create new superuser
    user = User.objects.create_superuser(
        email=email,
        password=password,
        display_name=display_name
    )
    print(f"✅ Superuser created successfully!")

print(f"\nSuperuser Details:")
print(f"Email: {user.email}")
print(f"Display Name: {user.display_name}")
print(f"Is Staff: {user.is_staff}")
print(f"Is Superuser: {user.is_superuser}")
print(f"\nYou can now login at:")
print(f"- Django Admin: http://127.0.0.1:9000/admin")
print(f"- Flask Frontend: http://127.0.0.1:5173/login")
