from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_approval_email(to_email, teammate_email, team_name, username, password):
    """
    Sends a styled HTML credentials email to both the primary registrant
    and the teammate (if they provided an email).
    """
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
    
    # Plain text version for email clients that do not render HTML
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
    
    # Construct the Django EmailMessage
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients
    )
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send(fail_silently=False)
        print(f"[Email] Approval credentials email sent successfully to {recipients}.")
        return True
    except Exception as e:
        print(f"[Email] Failed to send approval email to {recipients}: {e}")
        return False
