import os
import sys
import django

# Add the parent folder of scripts (backend) to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_backend.settings')
django.setup()

from django.contrib.auth.models import User

def main():
    # Filter all superusers and staff users
    admins = User.objects.filter(is_superuser=True) | User.objects.filter(is_staff=True)
    
    # If no admin users exist, create one
    if not admins.exists():
        username = 'admin'
        email = 'admin@example.com'
        password = 'infactRudraksh@2627!!'
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"No existing admin accounts found. Created a new superuser '{username}' with email '{email}'.")
        return
        
    count = 0
    new_password = 'infactRudraksh@2627!!'
    for user in list(admins):
        user.set_password(new_password)
        user.save()
        print(f"Updated password for admin user: {user.username}")
        count += 1
        
    print(f"\nSuccessfully updated password for {count} administrator account(s).")

if __name__ == '__main__':
    main()
