import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_backend.settings')
django.setup()

from registrations.models import TeamRegistration

def run():
    print("Testing Supabase Database Connection & Registration Insert...")
    
    test_email = "test.supabase.user@example.com"
    
    # Cleanup any existing test record
    TeamRegistration.objects.filter(primary_email=test_email).delete()
    
    # Create a test registration record
    test_reg = TeamRegistration.objects.create(
        primary_name="Supabase Tester",
        teammate_name="Partner Tester",
        primary_email=test_email,
        teammate_email="partner.supabase@example.com",
        primary_mobile="9876543210",
        teammate_mobile="9876543211",
        team_name="Supabase Tech Team",
        institution="Infacto Test Institute",
        experience="Debate enthusiast",
        payment_screenshot="https://res.cloudinary.com/demo/image/upload/sample.jpg",
        txn_id="TXN_SUPABASE_TEST_12345",
        add_merch=True,
        primary_tshirt_size="L",
        teammate_tshirt_size="M",
        referral_code="SUPABASE2026"
    )
    
    print(f"[SUCCESS] Successfully created TeamRegistration in Supabase! ID: {test_reg.id}")
    
    # Retrieve it back from Supabase
    fetched = TeamRegistration.objects.get(id=test_reg.id)
    print(f"[SUCCESS] Retrieved Record from Supabase:")
    print(f"   Team Name: {fetched.team_name}")
    print(f"   Primary Name: {fetched.primary_name}")
    print(f"   Primary Email: {fetched.primary_email}")
    print(f"   Txn ID: {fetched.txn_id}")
    
    # Clean up test registration
    fetched.delete()
    print("[SUCCESS] Cleaned up test record from Supabase database.")

if __name__ == '__main__':
    run()
