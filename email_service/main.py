import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)


# SMTP configurations from environment
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', '')

def send_approval_email(to_email, teammate_email, team_name, username, password):
    subject = f"Infacto 5.0 - Registration Approved (Team: {team_name})"
    
    # Recipient list
    recipients = [to_email]
    if teammate_email and teammate_email.strip():
        recipients.append(teammate_email.strip())

    # HTML Email Template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Infacto 5.0 Registration Approved</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #050505;
                color: #e5e7eb;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #0a0a0a;
                border: 1px solid #222222;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }}
            .header {{
                background-color: #000000;
                padding: 30px;
                text-align: center;
                border-bottom: 2px solid #ca8a04;
            }}
            .logo {{
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 2px;
                color: #ffffff;
                text-transform: uppercase;
                margin: 0;
            }}
            .highlight {{
                color: #eab308;
            }}
            .content {{
                padding: 40px 30px;
                line-height: 1.6;
            }}
            h1 {{
                font-size: 20px;
                color: #ffffff;
                margin-top: 0;
                margin-bottom: 20px;
            }}
            p {{
                margin: 0 0 20px 0;
                color: #d1d5db;
            }}
            .credentials-box {{
                background-color: #111111;
                border: 1px dashed #444444;
                border-radius: 8px;
                padding: 24px;
                margin: 30px 0;
            }}
            .cred-row {{
                display: flex;
                margin-bottom: 12px;
                font-size: 15px;
            }}
            .cred-row:last-child {{
                margin-bottom: 0;
            }}
            .cred-label {{
                font-weight: bold;
                color: #9ca3af;
                width: 140px;
                flex-shrink: 0;
            }}
            .cred-value {{
                color: #ffffff;
                font-family: 'Courier New', Courier, monospace;
                font-weight: bold;
            }}
            .btn-container {{
                text-align: center;
                margin: 30px 0 10px 0;
            }}
            .btn {{
                display: inline-block;
                background-color: #eab308;
                color: #000000 !important;
                text-decoration: none;
                padding: 14px 36px;
                font-weight: bold;
                border-radius: 30px;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 1px;
                transition: background-color 0.3s;
            }}
            .footer {{
                background-color: #080808;
                padding: 30px;
                text-align: center;
                font-size: 12px;
                color: #6b7280;
                border-top: 1px solid #1a1a1a;
            }}
            .footer a {{
                color: #9ca3af;
                text-decoration: none;
            }}
            .footer a:hover {{
                color: #ffffff;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">Infacto <span class="highlight">5.0</span></div>
            </div>
            <div class="content">
                <h1>Registration Approved!</h1>
                <p>Dear Team,</p>
                <p>We are excited to inform you that your registration for <strong>Infacto 5.0</strong> has been approved by the administrators.</p>
                <p>Use the following auto-generated credentials to access your participant dashboard. From the dashboard, you will be able to view your debate topic, stance, scheduled slots, and classroom assignments as they are updated.</p>
                
                <div class="credentials-box">
                    <div class="cred-row">
                        <span class="cred-label">Team Name:</span>
                        <span class="cred-value" style="font-family: inherit; font-weight: normal;">{team_name}</span>
                    </div>
                    <div class="cred-row">
                        <span class="cred-label">Login ID:</span>
                        <span class="cred-value">{username}</span>
                    </div>
                    <div class="cred-row">
                        <span class="cred-label">Password:</span>
                        <span class="cred-value">{password}</span>
                    </div>
                </div>

                <div class="btn-container">
                    <a href="https://infacto-six.vercel.app/login.html" class="btn" target="_blank">Access Dashboard</a>
                </div>
            </div>
            <div class="footer">
                <p>This is an automated email notification regarding your registration.</p>
                <p><strong>Questions or Support?</strong><br>
                Contact Rudraksh Gupta: +91 7060109792 | Aryan Srivastava: +91 9555611243<br>
                Or email us at: <a href="mailto:orator@iiitn.ac.in">orator@iiitn.ac.in</a></p>
                <p>&copy; 2026 Orator Club, IIIT Nagpur. All Rights Reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    Infacto 5.0 - Registration Approved!

    Dear Team,

    We are excited to inform you that your registration for Infacto 5.0 has been approved by the administrators.

    Here are your credentials to log in to your participant dashboard:

    Dashboard Link: https://infacto-six.vercel.app/login.html
    Team Name: {team_name}
    Login ID: {username}
    Password: {password}

    Please keep these details secure.

    For support, contact:
    - Rudraksh Gupta: +91 7060109792
    - Aryan Srivastava: +91 9555611243
    - Email: orator@iiitn.ac.in

    Orator Club, IIIT Nagpur
    """

    # Create Message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = DEFAULT_FROM_EMAIL or EMAIL_HOST_USER
    msg['To'] = ", ".join(recipients)

    # Attach parts
    part1 = MIMEText(text_content, 'plain')
    part2 = MIMEText(html_content, 'html')
    msg.attach(part1)
    msg.attach(part2)

    # Connect to server and send
    try:
        if EMAIL_USE_TLS:
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=30)
            server.starttls()
        else:
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=30)

        if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)

        server.sendmail(EMAIL_HOST_USER, recipients, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email to {recipients}: {e}")
        return False

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/send-email', methods=['POST'])
def handle_send_email():
    data = request.get_json() or {}
    to_email = data.get('to_email')
    teammate_email = data.get('teammate_email')
    team_name = data.get('team_name')
    username = data.get('username')
    password = data.get('password')

    if not all([to_email, team_name, username, password]):
        return jsonify({"status": "error", "message": "Missing required fields."}), 400

    # If SMTP username/password are not set, log and return fallback success (like console backend)
    if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
        print(f"[Console Fallback] Would have sent credentials to {to_email} and {teammate_email} for team '{team_name}'")
        return jsonify({"status": "success", "message": "Mock email output to console (credentials not configured)."}), 200

    success = send_approval_email(to_email, teammate_email, team_name, username, password)
    if success:
        return jsonify({"status": "success", "message": "Email sent successfully."}), 200
    else:
        return jsonify({"status": "error", "message": "SMTP transmission failed. Check server logs."}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    # Listen on all interfaces
    app.run(host='0.0.0.0', port=port, debug=True)
