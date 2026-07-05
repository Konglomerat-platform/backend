from django.test import TestCase
from rest_framework.test import APIClient

from apps.notifications.models import Notification
from apps.support.models import Complaint


class ComplaintApiTests(TestCase):
    def test_public_complaint_creates_admin_notification(self):
        response = APIClient().post(
            "/api/complaints/",
            {"name": "Visitor", "contact": "v@example.com", "text": "Need help"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Complaint.objects.count(), 1)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(response.data["from"], "Visitor")
