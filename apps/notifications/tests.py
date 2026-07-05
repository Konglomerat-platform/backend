from django.test import TestCase
from rest_framework.test import APIClient

from apps.companies.models import Company
from apps.notifications.models import Notification, NotificationRead
from apps.users.models import User


class NotificationApiTests(TestCase):
    def test_list_and_mark_read_for_company_user(self):
        company = Company.objects.create(name="Acme", slug="acme")
        user = User.objects.create_user(username="company", role=User.Role.COMPANY, company=company)
        Notification.objects.create(
            audience=Notification.Audience.COMPANY,
            target_company=company,
            title_i18n={"en": "Hello"},
            text="Message",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["unread"], 1)

        read = client.post("/api/notifications/read/")
        self.assertEqual(read.status_code, 200)
        self.assertEqual(NotificationRead.objects.count(), 1)
