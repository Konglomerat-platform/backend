from django.contrib.auth.hashers import make_password
from django.core.management import call_command
from django.test import TestCase

from apps.catalog.models import Product
from apps.communications.models import ChatMessage
from apps.companies.models import Company
from apps.users.models import User


class SeedSkipUsersTests(TestCase):
    """--skip-users must never touch credentials on a live deployment."""

    def test_skip_users_leaves_an_existing_admin_password_untouched(self):
        User.objects.create(
            username="admin",
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
            password=make_password("a-real-production-password"),
        )

        call_command("seed_demo_data", "--skip-users")

        admin = User.objects.get(username="admin")
        self.assertTrue(admin.check_password("a-real-production-password"))
        self.assertFalse(admin.check_password("12"))

    def test_skip_users_creates_no_accounts_and_no_chat_messages(self):
        call_command("seed_demo_data", "--skip-users")

        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(ChatMessage.objects.count(), 0)

    def test_skip_users_still_seeds_catalogue_content(self):
        call_command("seed_demo_data", "--skip-users")

        self.assertEqual(Company.objects.count(), 9)
        self.assertEqual(Product.objects.count(), 8)

    def test_default_invocation_still_provisions_the_demo_accounts(self):
        call_command("seed_demo_data")

        self.assertTrue(User.objects.get(username="admin").check_password("12"))
        self.assertTrue(User.objects.get(username="company1").check_password("12"))
        self.assertEqual(ChatMessage.objects.count(), 5)
