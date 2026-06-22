from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase


class InvalidatePasswordsTest(TestCase):
    def _make_user(self, username: str, password: str) -> User:
        user = User.objects.create_user(username=username, password=password)
        # Simulate an imported sha1 hash so it doesn't start with "!"
        user.password = f"sha1$salt${username}_hash"
        user.save(update_fields=["password"])
        return user

    def test_invalidates_sha1_passwords(self) -> None:
        user = self._make_user("sha1user", "irrelevant")
        call_command("invalidate_passwords")
        user.refresh_from_db()
        self.assertFalse(user.has_usable_password())

    def test_skips_superusers(self) -> None:
        superuser = User.objects.create_superuser(
            username="admin", password="adminpass"
        )
        superuser.password = "sha1$salt$adminhash"
        superuser.save(update_fields=["password"])
        call_command("invalidate_passwords")
        superuser.refresh_from_db()
        self.assertTrue(superuser.password.startswith("sha1"))

    def test_skips_already_invalidated(self) -> None:
        user = User.objects.create_user(username="nopwuser", password="x")
        user.set_unusable_password()
        user.save(update_fields=["password"])
        original_password = user.password
        call_command("invalidate_passwords")
        user.refresh_from_db()
        self.assertEqual(user.password, original_password)

    def test_count_output(self) -> None:
        self._make_user("u1", "x")
        self._make_user("u2", "x")
        from io import StringIO

        out = StringIO()
        call_command("invalidate_passwords", stdout=out)
        self.assertIn("2", out.getvalue())

    def test_skips_empty_password(self) -> None:
        user = User.objects.create_user(username="emptypass", password="x")
        user.password = ""
        user.save(update_fields=["password"])
        call_command("invalidate_passwords")
        user.refresh_from_db()
        self.assertEqual(user.password, "")
