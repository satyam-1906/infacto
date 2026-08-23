from django.apps import AppConfig
import os


class RegistrationsConfig(AppConfig):
    name = 'registrations'

    def ready(self):
        # Prevent spawning the thread twice during local auto-reload
        if os.environ.get('RUN_MAIN') == 'true' or not os.environ.get('RUN_MAIN'):
            from .keepalive import start_keepalive
            start_keepalive()
