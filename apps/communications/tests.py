from django.test import TestCase
from rest_framework.test import APIClient

from apps.communications.models import ChatMessage, ChatThread
from apps.companies.models import Company
from apps.users.models import User


class ChatApiTests(TestCase):
    def test_authenticated_user_can_send_group_message(self):
        user = User.objects.create_user(username="company", role=User.Role.COMPANY)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/chat/messages/", {"chat": "group", "text": "Hello"}, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ChatMessage.objects.count(), 1)
        self.assertEqual(response.data["chat"], "group")
        self.assertTrue(ChatThread.objects.filter(kind=ChatThread.Kind.GROUP).exists())

    def test_company_admin_thread_is_created_on_demand(self):
        company = Company.objects.create(name="Acme", slug="acme")
        user = User.objects.create_user(username="company", role=User.Role.COMPANY, company=company)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/chat/messages/", {"chat": "Acme", "text": "Hello admin"}, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            ChatThread.objects.filter(kind=ChatThread.Kind.ADMIN_COMPANY, company=company).exists()
        )
