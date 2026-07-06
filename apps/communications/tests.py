from urllib.parse import urlparse

from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.communications.models import ChatMessage, ChatThread
from apps.companies.models import Company
from core.asgi import application
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

    def test_multipart_upload_preserves_file_metadata_and_download_name(self):
        user = User.objects.create_user(username="company", role=User.Role.COMPANY)
        client = APIClient()
        client.force_authenticate(user=user)
        upload = SimpleUploadedFile(
            "cards (1).pdf",
            b"%PDF-1.4",
            content_type="application/pdf",
        )

        response = client.post(
            "/api/chat/messages/",
            {"chat": "group", "kind": "file", "text": "caption", "file": upload},
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "cards (1).pdf")
        self.assertEqual(response.data["contentType"], "application/pdf")
        self.assertEqual(response.data["size"], 8)
        self.assertIn("/api/chat/messages/", response.data["downloadUrl"])

        download = client.get(urlparse(response.data["downloadUrl"]).path)
        self.assertEqual(download.status_code, 200)
        self.assertEqual(download["Content-Type"], "application/pdf")
        self.assertIn("cards", download["Content-Disposition"])
        self.assertIn(".pdf", download["Content-Disposition"])

    def test_reply_parent_must_belong_to_same_thread(self):
        company = Company.objects.create(name="Acme", slug="acme")
        user = User.objects.create_user(username="company", role=User.Role.COMPANY, company=company)
        other = User.objects.create_user(username="other", role=User.Role.COMPANY)
        parent = ChatMessage.objects.create(
            thread=ChatThread.objects.create(kind=ChatThread.Kind.GROUP, title="Group"),
            sender=other,
            text="Group message",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/chat/messages/",
            {"chat": "Acme", "text": "Wrong parent", "parent": str(parent.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    async def test_websocket_rejects_missing_token(self):
        communicator = WebsocketCommunicator(application, "/ws/chat/?chat=group")
        connected, _ = await communicator.connect()
        self.assertFalse(connected)

    async def test_websocket_accepts_valid_token_for_allowed_chat(self):
        user = await database_sync_to_async(User.objects.create_user)(
            username="company",
            role=User.Role.COMPANY,
        )
        token = await database_sync_to_async(lambda: str(RefreshToken.for_user(user).access_token))()
        communicator = WebsocketCommunicator(application, f"/ws/chat/?chat=group&token={token}")

        connected, _ = await communicator.connect()

        self.assertTrue(connected)
        await communicator.disconnect()
