from django.db import models


class ChatThread(models.Model):
    class Kind(models.TextChoices):
        GROUP = "group", "Group"
        ADMIN_COMPANY = "admin_company", "Admin-company"

    kind = models.CharField(max_length=32, choices=Kind.choices)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chat_threads",
    )
    title = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["kind", "company"],
                condition=models.Q(company__isnull=False),
                name="unique_company_thread_kind",
            )
        ]

    def __str__(self) -> str:
        return self.title or self.kind


class ChatMessage(models.Model):
    class Kind(models.TextChoices):
        TEXT = "text", "Text"
        IMAGE = "image", "Image"
        FILE = "file", "File"
        VOICE = "voice", "Voice"

    legacy_id = models.CharField(max_length=40, blank=True, unique=True, null=True)
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="chat_messages")
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.TEXT)
    text = models.TextField(blank=True)
    file = models.FileField(upload_to="chat/", blank=True)
    name = models.CharField(max_length=200, blank=True)
    duration_seconds = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "id"]


class MessageReceipt(models.Model):
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="receipts")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="message_receipts")
    seen_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["message", "user"], name="unique_message_receipt")
        ]
