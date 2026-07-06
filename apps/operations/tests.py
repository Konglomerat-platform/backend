from django.test import TestCase
from rest_framework.test import APIClient

from apps.notifications.models import Notification
from apps.operations.models import Conference
from apps.users.models import User


class ConferenceApiTests(TestCase):
    def test_create_conference_normalizes_bare_link_and_notifies_companies(self):
        admin = User.objects.create_user(username="admin", role=User.Role.ADMIN)
        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.post(
            "/api/conferences/",
            {"name": "Meet", "date": "2026-07-08", "time": "10:00", "link": "meet.google.com/abc"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["link"], "https://meet.google.com/abc")
        self.assertEqual(Conference.objects.get().link, "https://meet.google.com/abc")
        self.assertEqual(Notification.objects.get().link, "https://meet.google.com/abc")
