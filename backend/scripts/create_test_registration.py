import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_backend.settings')
django.setup()

from registrations.models import TeamRegistration

def run():
    print("Creating Test Registration in Supabase Database...")
    
    test_email = "alex.rivera@infacto.test"
    
    # Remove any previous test with this email to avoid unique constraint error
    TeamRegistration.objects.filter(primary_email=test_email).delete()
    
    # Create persistent test registration
    reg = TeamRegistration.objects.create(
        primary_name="Alex Rivera",
        teammate_name="Jordan Lee",
        primary_email=test_email,
        teammate_email="jordan.lee@infacto.test",
        primary_mobile="+19876543210",
        teammate_mobile="+19876543211",
        team_name="Team Zenith",
        institution="Stanford University",
        experience="2 years varsity parliamentary debate",
        payment_screenshot="https://res.cloudinary.com/k56sdihn/image/upload/v1/samples/payment_test.jpg",
        txn_id="TXN_SUPABASE_998877",
        is_approved=False,
        add_merch=True,
        primary_tshirt_size="L",
        teammate_tshirt_size="M",
        referral_code="SUPABASE_GO"
    )
    
    print("[SUCCESS] Test Registration created successfully in Supabase PostgreSQL!")
    print(f"  Record ID          : {reg.id}")
    print(f"  Team Name          : {reg.team_name}")
    print(f"  Primary Delegate   : {reg.primary_name} ({reg.primary_email})")
    print(f"  Teammate Delegate  : {reg.teammate_name} ({reg.teammate_email})")
    print(f"  Institution        : {reg.institution}")
    print(f"  Transaction ID     : {reg.txn_id}")
    print(f"  Payment Screenshot : {reg.payment_screenshot}")
    print(f"  Merchandise        : {reg.add_merch} (Primary: {reg.primary_tshirt_size}, Teammate: {reg.teammate_tshirt_size})")
    print(f"  Approval Status    : {'Approved' if reg.is_approved else 'Pending Approval'}")
    print("\nRecord is saved and persistent in Supabase table 'registrations_teamregistration'.")

if __name__ == '__main__':
    run()
