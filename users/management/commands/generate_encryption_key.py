from django.core.management.base import BaseCommand
from cryptography.fernet import Fernet

class Command(BaseCommand):
    help = 'Generate a secure encryption key for router passwords'

    def handle(self, *args, **options):
        """Generate and display a new encryption key"""
        key = Fernet.generate_key()
        self.stdout.write(
            self.style.SUCCESS(f'Generated encryption key: {key.decode()}')
        )
        self.stdout.write(
            self.style.WARNING(
                'Copy this key and update your settings.py ENCRYPTION_KEY variable'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                'Keep this key secure and never commit it to version control'
            )
        )
