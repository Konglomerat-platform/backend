from django.db import models


class RndSubmission(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    legacy_id = models.CharField(max_length=40, blank=True, unique=True, null=True)
    company = models.ForeignKey("companies.Company", on_delete=models.PROTECT, related_name="rnd_submissions")
    category = models.CharField(max_length=120, blank=True)
    name_i18n = models.JSONField(default=dict)
    description_i18n = models.JSONField(default=dict, blank=True)
    patent_requested = models.BooleanField(default=False)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_rnd_submissions",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
