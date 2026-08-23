# Infacto Django Backend

This backend application powers the "Infacto" debate competition registration system. Built with Django and vanilla JavaScript fetch APIs on the frontend, it bridges the gap between public web signups and administrative management.

## Core Capabilities

1. **API Endpoints (Registrations)**
   - Exposes `http://127.0.0.1:8001/api/register/` to securely accept automated `POST` requests from the external HTML frontend.
   - Extracts all user text inputs (names, emails, phone numbers, institution, experience).
   - Extracts binary image payloads for **payment screenshots**.
   - Bypasses local CSRF blocks during testing across different localhost ports utilizing `django-cors-headers`.
   - Saves all form data into the SQLite database under a "Pending" (`is_approved=False`) state.

2. **Admin Dashboard (Moderation)**
   - Superuser dashboard available at `http://127.0.0.1:8001/admin/`.
   - Displays a clean visual table of all registered teams via `TeamRegistrationAdmin`.
   - Allows administrators to click and visually verify payment screenshots explicitly routed through local media storage `/media/screenshots/`.

3. **Automated Credential Generation**
   - Through a custom written admin-action (`Approve selected teams and generate credentials`), administrators can select multiple teams in bulk.
   - Automatically generates a safe, unique `login_id` based off the team name (resolving duplicates).
   - Generates a completely secure, random 8-character alphanumeric password for each team.
   - Uses Django's `User` model to physically create authentication accounts for each team in the background.

4. **Dynamic Excel Data Export**
   - Integrates with the `openpyxl` Python library.
   - At the exact moment of team approval, silently opens (or creates if missing) a master spreadsheet named `infacto_participants.xlsx` inside the project root folder.
   - Appends all 10 column data points containing names, detailed contact info, and their **newly generated login IDs and Passwords**, drastically optimizing manual bookkeeping.

## Setup & Running Locally

Because the frontend is running on Port 8000 (Python's default HTTP server), this Django backend has been explicitly mapped to run on **Port 8001** to prevent conflicts.

To start the server, move into the `main_backend` folder and run:
`python manage.py runserver 8001`
