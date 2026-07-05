from django.db import models


class Notification(models.Model):
    class Audience(models.TextChoices):
        ADMIN = "admin", "Admin"
        COMPANY = "company", "Company"

    audience = models.CharField(max_length=24, choices=Audience.choices)
    target_company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    title_i18n = models.JSONField(default=dict)
    text = models.TextField(blank=True)
    link = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]


class NotificationRead(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="reads")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="notification_reads")
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["notification", "user"], name="unique_notification_read")
        ]
