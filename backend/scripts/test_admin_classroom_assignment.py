import os
import sys
import django
import json

# Setup Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from registrations.models import TeamRegistration
from registrations.views import candidate_login, update_assignment

def run():
    print("=== Admin Login & Classroom Assignment Test on Supabase ===")
    
    # 1. Provision Admin Account in Supabase
    admin_username = 'admin'
    admin_password = 'infactRudraksh@2627!!'
    
    admin_user, _ = User.objects.get_or_create(
        username=admin_username,
        defaults={'email': 'admin@infacto.in', 'is_staff': True, 'is_superuser': True}
    )
    admin_user.set_password(admin_password)
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    print(f"[AUTH] Superuser '{admin_username}' provisioned in Supabase PostgreSQL.")

    # 2. Perform Admin Login via API (/api/login/)
    rf = RequestFactory()
    login_req = rf.post(
        '/api/login/',
        data=json.dumps({"username": admin_username, "password": admin_password}),
        content_type='application/json'
    )
    SessionMiddleware(lambda r: None).process_request(login_req)
    login_req.session.save()

    login_resp = candidate_login(login_req)
    login_data = json.loads(login_resp.content.decode('utf-8'))
    
    print("\n[ADMIN LOGIN API RESULT]")
    print(f"  Status      : {login_data.get('status')}")
    print(f"  Is Admin    : {login_data.get('is_admin')}")
    admin_token = login_data.get('admin_token')
    print(f"  Admin Token : {admin_token}")

    # 3. Retrieve target team registration from Supabase
    team = TeamRegistration.objects.get(team_name="Team Zenith")
    print(f"\n[TARGET REGISTRATION IN SUPABASE]")
    print(f"  Team ID          : {team.id}")
    print(f"  Team Name        : {team.team_name}")
    print(f"  Classroom BEFORE : {team.classroom}")

    # 4. Assign Classroom and Debate Details via Admin API (/api/update-assignment/)
    new_classroom = "Room 405 - Science Block"
    new_topic = "Future of AI in Education"
    new_stance = "AGAINST"
    new_date = "2026-09-20"
    new_time = "02:00 PM IST"

    assignment_payload = json.dumps({
        "id": team.id,
        "classroom": new_classroom,
        "debate_topic": new_topic,
        "stance": new_stance,
        "debate_date": new_date,
        "debate_time": new_time
    })

    assign_req = rf.post(
        '/api/update-assignment/',
        data=assignment_payload,
        content_type='application/json',
        HTTP_X_ADMIN_TOKEN=admin_token
    )

    assign_resp = update_assignment(assign_req)
    assign_result = json.loads(assign_resp.content.decode('utf-8'))

    print("\n[ASSIGNMENT API RESULT]")
    print(f"  Status  : {assign_result.get('status')}")
    print(f"  Message : {assign_result.get('message')}")
    print(f"  Data    : {json.dumps(assign_result.get('data'), indent=4)}")

    # 5. Direct Supabase Query Verification
    team.refresh_from_db()
    print("\n[SUPABASE DB PERSISTENCE VERIFICATION]")
    print(f"  Classroom AFTER : {team.classroom}")
    print(f"  Topic AFTER     : {team.debate_topic}")
    print(f"  Stance AFTER    : {team.stance}")
    print(f"  Date AFTER      : {team.debate_date}")
    print(f"  Time AFTER      : {team.debate_time}")

    assert team.classroom == new_classroom, "Classroom failed to update in Supabase!"
    print("\n[SUCCESS] Admin authenticated, token issued, and classroom assigned directly in Supabase PostgreSQL!")

if __name__ == '__main__':
    run()
