import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create a superuser with admin profile from environment variables (for Render)'

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model
        from accounts.models import UserProfile

        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpassword')

        try:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'is_staff': True, 'is_superuser': True}
            )

            # Always sync password, email and flags in case they changed
            user.set_password(password)
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created superuser "{username}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Updated existing superuser "{username}"'))

            # Ensure a UserProfile with role=admin exists
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = 'admin'
            profile.is_approved = True
            profile.save()
            self.stdout.write(self.style.SUCCESS(f'Admin profile set for "{username}"'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating superuser: {e}'))
            raise
