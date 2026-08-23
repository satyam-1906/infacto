from django.core.management.base import BaseCommand
from registrations.emails import send_approval_email

class Command(BaseCommand):
    help = 'Sends registration approval credentials email'

    def add_arguments(self, parser):
        parser.add_argument('to_email', type=str)
        parser.add_argument('teammate_email', type=str)
        parser.add_argument('team_name', type=str)
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **options):
        to_email = options['to_email']
        teammate_email = options['teammate_email']
        team_name = options['team_name']
        username = options['username']
        password = options['password']

        # Handle empty/none string placeholders from command line
        if teammate_email.lower() in ('none', 'null', ''):
            teammate_email = None

        self.stdout.write(f"Sending approval email process started for team '{team_name}'...")
        success = send_approval_email(
            to_email=to_email,
            teammate_email=teammate_email,
            team_name=team_name,
            username=username,
            password=password
        )
        if success:
            self.stdout.write(self.style.SUCCESS("Email sent successfully."))
        else:
            self.stdout.write(self.style.ERROR("Failed to send email."))
