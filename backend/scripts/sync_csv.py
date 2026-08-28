import os
import sys
import csv
import django

# Add the parent folder of scripts (backend) to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_backend.settings')
django.setup()

from registrations.models import TeamRegistration
from django.contrib.auth.models import User

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'infacto_registrations_2026-08-28.csv'))

def sync():
    if not os.path.exists(CSV_PATH):
        print(f"CSV file not found at: {CSV_PATH}")
        return

    created_count = 0
    updated_count = 0

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_id = int(row['ID']) if row.get('ID') else None
            primary_email = row['Primary Email'].strip()

            # Find by ID or primary_email
            reg = None
            if row_id:
                reg = TeamRegistration.objects.filter(id=row_id).first()
            if not reg:
                reg = TeamRegistration.objects.filter(primary_email__iexact=primary_email).first()

            is_new = reg is None

            # Maps
            add_merch = row['Merch'].strip().lower() in ('yes', 'true', 'on', '1')
            status_lower = row['Status'].strip().lower()
            is_approved = status_lower == 'approved' or status_lower == 'yes' or status_lower == 'true'

            # Load fields
            fields = {
                'team_name': row['Team Name'].strip(),
                'primary_name': row['Primary Name'].strip(),
                'primary_email': primary_email,
                'primary_mobile': row['Primary Mobile'].strip(),
                'teammate_name': row['Teammate Name'].strip() if row.get('Teammate Name') else '',
                'teammate_email': row['Teammate Email'].strip() if row.get('Teammate Email') else '',
                'teammate_mobile': row['Teammate Mobile'].strip() if row.get('Teammate Mobile') else '',
                'institution': row['Institution'].strip(),
                'experience': row['Experience'].strip() if row.get('Experience') else '',
                'add_merch': add_merch,
                'primary_tshirt_size': row['Primary Size'].strip() if row.get('Primary Size') else '',
                'teammate_tshirt_size': row['Teammate Size'].strip() if row.get('Teammate Size') else '',
                'referral_code': row['Referral Code'].strip() if row.get('Referral Code') else '',
                'debate_topic': row['Debate Topic'].strip() if row.get('Debate Topic') else 'Waiting for Assignment...',
                'stance': row['Stance'].strip() if row.get('Stance') else 'Pending',
                'debate_date': row['Date'].strip() if row.get('Date') else 'TBD',
                'debate_time': row['Time'].strip() if row.get('Time') else 'TBD',
                'classroom': row['Classroom'].strip() if row.get('Classroom') else 'TBD',
                'is_approved': is_approved,
                'generated_username': row['Login ID'].strip() if row.get('Login ID') else '',
                'generated_password': row['Password'].strip() if row.get('Password') else '',
                'payment_screenshot': row['Payment URL'].strip() if row.get('Payment URL') else '',
                'txn_id': None,  # Always set txn_id as None for CSV imports
            }

            if is_new:
                if row_id:
                    fields['id'] = row_id
                reg = TeamRegistration.objects.create(**fields)
                created_count += 1
                action = "Created"
            else:
                for k, v in fields.items():
                    setattr(reg, k, v)
                reg.save()
                updated_count += 1
                action = "Updated"

            # Sync linked Django User if approved and username/password exist
            if reg.is_approved and reg.generated_username and reg.generated_password:
                if not User.objects.filter(username=reg.generated_username).exists():
                    User.objects.create_user(
                        username=reg.generated_username,
                        email=reg.primary_email,
                        password=reg.generated_password
                    )
                    print(f"  -> Created linked Django User: {reg.generated_username}")

            print(f"[{action}] Team ID: {reg.id}")

    print(f"\nDone! Sync summary: Created={created_count}, Updated={updated_count}")

if __name__ == '__main__':
    sync()
