from django.db import models


class Complaint(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RESOLVED = "resolved", "Resolved"

    legacy_id = models.CharField(max_length=40, blank=True, unique=True, null=True)
    from_company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="complaints",
    )
    from_name = models.CharField(max_length=180, blank=True)
    contact = models.CharField(max_length=180, blank=True)
    subject_i18n = models.JSONField(default=dict, blank=True)
    message_i18n = models.JSONField(default=dict, blank=True)
    raw_message = models.TextField(blank=True)
    official = models.BooleanField(default=False)
    reply = models.TextField(blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]


class ComplaintAttachment(models.Model):
    class Kind(models.TextChoices):
        IMAGE = "image", "Image"
        FILE = "file", "File"
        VOICE = "voice", "Voice"

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="attachments")
    kind = models.CharField(max_length=16, choices=Kind.choices)
    file = models.FileField(upload_to="complaints/")
    name = models.CharField(max_length=200, blank=True)
    duration_seconds = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
