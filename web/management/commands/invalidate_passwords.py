from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Set all user passwords as unusable, requiring a manual reset."

    def handle(self, *args: str, **options: str) -> None:
        users = User.objects.exclude(password="").exclude(is_superuser=True)
        count = 0
        for user in users:
            if not user.password.startswith("!"):
                user.set_unusable_password()
                user.save(update_fields=["password"])
                count += 1
        self.stdout.write(
            self.style.SUCCESS(f"Invalidated passwords for {count} users.")
        )
