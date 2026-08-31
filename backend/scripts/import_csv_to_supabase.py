import csv
import io
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_backend.settings')
django.setup()

from django.db import connection
from registrations.models import TeamRegistration

CSV_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'infacto_registrations_2026-08-30.csv')
SQL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'import_registrations_2026-08-30.sql')

def esc(val):
    if val is None or str(val).strip() == "":
        return "NULL"
    return "'" + str(val).replace("'", "''") + "'"

def run():
    print("Reading CSV...", flush=True)

    # Read entire file then parse — handles embedded newlines in fields
    with open(CSV_PATH, mode='r', encoding='utf-8-sig', newline='') as f:
        raw = f.read()

    reader = csv.DictReader(io.StringIO(raw))
    rows = list(reader)
    print(f"Parsed {len(rows)} rows from CSV.", flush=True)

    sql_parts = []
    objs = []

    for row in rows:
        primary_email = row.get('Primary Email', '').strip()
        if not primary_email:
            continue

        reg_id        = row.get('ID', '').strip()
        primary_name  = row.get('Primary Name', '').strip()
        teammate_name = row.get('Teammate Name', '').strip()
        teammate_email= row.get('Teammate Email', '').strip()
        primary_mobile= row.get('Primary Mobile', '').strip()
        teammate_mobile=row.get('Teammate Mobile', '').strip()
        team_name     = row.get('Team Name', '').strip()
        institution   = row.get('Institution', '').strip()
        experience    = row.get('Experience', '').strip()
        payment_url   = row.get('Payment URL', '').strip()
        referral_code = row.get('Referral Code', '').strip()
        add_merch     = row.get('Merch', '').strip().lower() == 'yes'
        p_size        = row.get('Primary Size', '').strip()
        t_size        = row.get('Teammate Size', '').strip()
        debate_topic  = row.get('Debate Topic', '').strip() or 'Waiting for Assignment...'
        stance        = row.get('Stance', '').strip() or 'Pending'
        debate_date   = row.get('Date', '').strip() or 'TBD'
        debate_time   = row.get('Time', '').strip() or 'TBD'
        classroom     = row.get('Classroom', '').strip() or 'TBD'
        is_approved   = row.get('Status', '').strip().lower() == 'approved'
        gen_username  = row.get('Login ID', '').strip()
        gen_password  = row.get('Password', '').strip()
        id_val        = int(reg_id) if reg_id.isdigit() else None
        merch_str     = "TRUE" if add_merch else "FALSE"
        appr_str      = "TRUE" if is_approved else "FALSE"
        id_sql        = str(id_val) if id_val else "DEFAULT"

        sql_parts.append(
            f"INSERT INTO public.registrations_teamregistration "
            f"(id,primary_name,teammate_name,primary_email,teammate_email,"
            f"primary_mobile,teammate_mobile,team_name,institution,experience,"
            f"payment_screenshot,add_merch,primary_tshirt_size,teammate_tshirt_size,"
            f"referral_code,debate_topic,stance,debate_date,debate_time,"
            f"classroom,is_approved,generated_username,generated_password) "
            f"VALUES ("
            f"{id_sql},{esc(primary_name)},{esc(teammate_name)},{esc(primary_email)},{esc(teammate_email)},"
            f"{esc(primary_mobile)},{esc(teammate_mobile)},{esc(team_name)},{esc(institution)},{esc(experience)},"
            f"{esc(payment_url)},{merch_str},{esc(p_size)},{esc(t_size)},"
            f"{esc(referral_code)},{esc(debate_topic)},{esc(stance)},{esc(debate_date)},{esc(debate_time)},"
            f"{esc(classroom)},{appr_str},{esc(gen_username)},{esc(gen_password)}"
            f") ON CONFLICT (primary_email) DO UPDATE SET "
            f"primary_name=EXCLUDED.primary_name,teammate_name=EXCLUDED.teammate_name,"
            f"teammate_email=EXCLUDED.teammate_email,primary_mobile=EXCLUDED.primary_mobile,"
            f"teammate_mobile=EXCLUDED.teammate_mobile,team_name=EXCLUDED.team_name,"
            f"institution=EXCLUDED.institution,experience=EXCLUDED.experience,"
            f"payment_screenshot=EXCLUDED.payment_screenshot,add_merch=EXCLUDED.add_merch,"
            f"primary_tshirt_size=EXCLUDED.primary_tshirt_size,teammate_tshirt_size=EXCLUDED.teammate_tshirt_size,"
            f"referral_code=EXCLUDED.referral_code,debate_topic=EXCLUDED.debate_topic,"
            f"stance=EXCLUDED.stance,debate_date=EXCLUDED.debate_date,debate_time=EXCLUDED.debate_time,"
            f"classroom=EXCLUDED.classroom,is_approved=EXCLUDED.is_approved,"
            f"generated_username=EXCLUDED.generated_username,generated_password=EXCLUDED.generated_password"
        )

        objs.append(TeamRegistration(
            primary_name=primary_name, teammate_name=teammate_name or None,
            primary_email=primary_email, teammate_email=teammate_email or None,
            primary_mobile=primary_mobile, teammate_mobile=teammate_mobile or None,
            team_name=team_name, institution=institution,
            experience=experience or None,
            payment_screenshot=payment_url or None,
            add_merch=add_merch,
            primary_tshirt_size=p_size or None, teammate_tshirt_size=t_size or None,
            referral_code=referral_code or None,
            debate_topic=debate_topic, stance=stance,
            debate_date=debate_date, debate_time=debate_time,
            classroom=classroom, is_approved=is_approved,
            generated_username=gen_username or None,
            generated_password=gen_password or None,
        ))

    # Save SQL file for reference
    sql_content = "-- import_registrations_2026-08-30.sql\n\n" + ";\n".join(sql_parts) + ";\n\n"
    sql_content += (
        "-- Sync identity sequence\n"
        "SELECT setval(pg_get_serialsequence('public.registrations_teamregistration','id'),"
        "(SELECT MAX(id) FROM public.registrations_teamregistration));\n"
    )
    with open(SQL_PATH, 'w', encoding='utf-8') as f:
        f.write(sql_content)
    print(f"SQL file saved: {os.path.abspath(SQL_PATH)}", flush=True)

    # Use bulk_create with update_conflicts — single DB round-trip, no model.save() overrides
    update_fields = [
        'primary_name','teammate_name','teammate_email','primary_mobile','teammate_mobile',
        'team_name','institution','experience','payment_screenshot','add_merch',
        'primary_tshirt_size','teammate_tshirt_size','referral_code',
        'debate_topic','stance','debate_date','debate_time','classroom',
        'is_approved','generated_username','generated_password'
    ]
    print(f"Bulk upserting {len(objs)} records via bulk_create (single round-trip)...", flush=True)
    result = TeamRegistration.objects.bulk_create(
        objs,
        update_conflicts=True,
        unique_fields=['primary_email'],
        update_fields=update_fields,
        batch_size=100
    )
    print(f"Bulk upsert complete. Rows affected: {len(result)}", flush=True)

    # Sync sequence
    with connection.cursor() as cur:
        cur.execute(
            "SELECT setval(pg_get_serialsequence('registrations_teamregistration','id'),"
            "(SELECT MAX(id) FROM registrations_teamregistration))"
        )
    total = TeamRegistration.objects.count()
    print(f"\n[DONE] Total records now in Supabase: {total}", flush=True)
    print(f"SQL script also saved at: {os.path.abspath(SQL_PATH)}", flush=True)

if __name__ == '__main__':
    run()
