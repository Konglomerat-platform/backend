from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient

from apps.companies.models import Company
from apps.users.models import User


class AuthApiTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Acme", slug="acme")
        self.user = User.objects.create_user(
            username="company",
            password="pass12345",
            role=User.Role.COMPANY,
            company=self.company,
            display_name="Acme User",
        )
        self.client = APIClient()

    def test_login_sets_refresh_cookie_and_me_returns_payload(self):
        response = self.client.post("/api/auth/login/", {"username": "company", "password": "pass12345"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(settings.JWT_REFRESH_COOKIE_NAME, response.cookies)
        token = response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        me = self.client.get("/api/auth/me/")

        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data["user"]["role"], User.Role.COMPANY)
        self.assertEqual(me.data["user"]["company"]["slug"], "acme")


class StorageSettingsTests(TestCase):
    def test_test_settings_use_local_storage(self):
        self.assertFalse(settings.USE_S3)
        self.assertEqual(
            settings.STORAGES["default"]["BACKEND"],
            "django.core.files.storage.FileSystemStorage",
        )
