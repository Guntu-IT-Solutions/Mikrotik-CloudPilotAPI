from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from payments.models import PaymentCredentials


class Command(BaseCommand):
    help = 'Fix payment credentials encryption issues by allowing re-encryption of private keys'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username or email of the user whose credentials need fixing',
        )
        parser.add_argument(
            '--provider',
            type=str,
            choices=['instasend', 'kopokopo'],
            default='instasend',
            help='Payment provider (default: instasend)',
        )
        parser.add_argument(
            '--private-key',
            type=str,
            help='New private key to encrypt and store',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all payment credentials',
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_credentials()
            return

        if not options['user']:
            raise CommandError('--user is required when not using --list')

        if not options['private_key']:
            raise CommandError('--private-key is required to fix credentials')

        self.fix_credentials(
            options['user'],
            options['provider'],
            options['private_key']
        )

    def list_credentials(self):
        """List all payment credentials"""
        self.stdout.write(self.style.SUCCESS('=== Payment Credentials ==='))
        
        credentials = PaymentCredentials.objects.all().order_by('user__username', 'provider')
        
        if not credentials:
            self.stdout.write(self.style.WARNING('No payment credentials found'))
            return

        for cred in credentials:
            status = '✓' if self.test_credentials(cred) else '✗'
            self.stdout.write(
                f"{status} {cred.user.username} - {cred.provider} ({cred.environment}) - "
                f"ID: {cred.id} - Active: {cred.is_active}"
            )

    def test_credentials(self, credentials):
        """Test if credentials can be decrypted"""
        try:
            credentials.get_private_key()
            return True
        except Exception:
            return False

    def fix_credentials(self, user_identifier, provider, private_key):
        """Fix payment credentials by re-encrypting the private key"""
        try:
            # Find user by username or email
            try:
                user = User.objects.get(username=user_identifier)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=user_identifier)
                except User.DoesNotExist:
                    raise CommandError(f'User not found: {user_identifier}')
        except Exception as e:
            raise CommandError(f'Error finding user: {e}')

        # Find credentials
        try:
            credentials = PaymentCredentials.objects.get(
                user=user,
                provider=provider
            )
        except PaymentCredentials.DoesNotExist:
            raise CommandError(
                f'No {provider} credentials found for user {user.username}'
            )

        # Test current credentials
        current_works = self.test_credentials(credentials)
        self.stdout.write(
            f"Current credentials status: {'✓ Working' if current_works else '✗ Broken'}"
        )

        if current_works:
            self.stdout.write(
                self.style.WARNING('Credentials are already working. No fix needed.')
            )
            return

        # Fix the credentials
        try:
            credentials.set_private_key(private_key)
            credentials.save()
            
            # Test the fix
            if self.test_credentials(credentials):
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Successfully fixed {provider} credentials for {user.username}'
                    )
                )
            else:
                raise CommandError('Fix failed - credentials still not working')
                
        except Exception as e:
            raise CommandError(f'Failed to fix credentials: {e}')
