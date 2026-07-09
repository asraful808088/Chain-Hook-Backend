from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Client

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with default test clients for verification'

    def handle(self, *args, **options):
        # 1. Create a default owner user if not exists
        owner_email = 'developer@chainhook.com'
        owner, created = User.objects.get_or_create(
            email=owner_email,
            defaults={
                'name': 'Lead Developer',
                'is_staff': True,
                'is_admin': True,
                'is_active': True
            }
        )
        if created:
            owner.set_password('developer123')
            owner.save()
            self.stdout.write(self.style.SUCCESS(f"Created developer user: {owner_email} with password: developer123"))
        else:
            self.stdout.write(self.style.WARNING(f"Developer user {owner_email} already exists."))

        # 2. Seed 'Nova Store' client
        client_nova, created_nova = Client.objects.update_or_create(
            name='Nova Store',
            defaults={
                'user': owner,
                'base_url': 'MerchantSandbox',
                'for_login': True,
                'for_payment': True,
                'is_active': True,
            }
        )
        self.stdout.write(self.style.SUCCESS(f"Nova Store Client seeded (created: {created_nova}). Base URL: 'MerchantSandbox'"))

        # 3. Seed 'Chain Hook' client
        client_ch, created_ch = Client.objects.update_or_create(
            name='Chain Hook',
            defaults={
                'user': owner,
                'base_url': 'http://localhost',
                'for_login': True,
                'for_payment': False,
                'is_active': True,
            }
        )
        self.stdout.write(self.style.SUCCESS(f"Chain Hook Client seeded (created: {created_ch}). Base URL: 'http://localhost'"))
