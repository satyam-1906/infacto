import os
import sys
import urllib.parse
import psycopg2
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

def run():
    db_url = os.getenv('DATABASE_URL')
    sql_path = os.path.join(BASE_DIR, '..', 'import_registrations_2026-08-30.sql')
    
    print(f"Connecting to Supabase PostgreSQL...", flush=True)
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    print(f"Reading SQL file: {sql_path}...", flush=True)
    with open(sql_path, encoding='utf-8') as f:
        full_sql = f.read()

    statements = [stmt.strip() for stmt in full_sql.split(';') if stmt.strip() and not stmt.strip().startswith('--')]

    print(f"Executing {len(statements)} SQL statements directly on Supabase...", flush=True)
    success = 0
    for i, stmt in enumerate(statements, 1):
        if stmt.upper().startswith('INSERT') or stmt.upper().startswith('SELECT'):
            try:
                cur.execute(stmt)
                success += 1
            except Exception as e:
                print(f"⚠️ Statement {i} warning: {e}", flush=True)

    cur.close()
    conn.close()
    print(f"\n[SUCCESS] Successfully executed {success} SQL statements in Supabase!", flush=True)

if __name__ == '__main__':
    run()
