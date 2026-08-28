import os
import sys
import django

# Add the parent folder of scripts (backend) to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_backend.settings')
django.setup()

from registrations.models import TeamRegistration
from django.contrib.auth.models import User

def main():
    # Get the first 14 registrations ordered by id ascending
    regs_to_delete = TeamRegistration.objects.all().order_by('id')[:14]
    
    count = 0
    for reg in list(regs_to_delete):
        reg_id = reg.id
        team_name = reg.team_name
        generated_username = reg.generated_username
        
        # Delete linked User if exists
        if generated_username:
            User.objects.filter(username=generated_username).delete()
            print(f"  -> Deleted User credentials: {generated_username}")
            
        reg.delete()
        print(f"Deleted registration: {team_name} (ID: {reg_id})")
        count += 1
        
    print(f"\nSuccessfully deleted {count} registrations.")

if __name__ == '__main__':
    main()
