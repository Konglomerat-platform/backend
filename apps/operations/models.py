from django.db import models


class Conference(models.Model):
    legacy_id = models.CharField(max_length=40, blank=True, unique=True, null=True)
    name = models.CharField(max_length=180)
    date = models.DateField()
    time = models.TimeField()
    description = models.TextField(blank=True)
    link = models.URLField(blank=True)
    capacity_total = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "time", "-created_at"]


class ConferenceAttendance(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name="attendances")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="conference_attendances")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["conference", "user"], name="unique_conference_attendance")
        ]


class ManagementModule(models.Model):
    key = models.CharField(max_length=80, unique=True)
    block_index = models.PositiveSmallIntegerField()
    module_index = models.PositiveSmallIntegerField()
    enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["block_index", "module_index"]


class Report(models.Model):
    class Scope(models.TextChoices):
        ALL = "all", "All"
        COMPANY = "company", "Company"

    scope = models.CharField(max_length=16, choices=Scope.choices)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
    )
    generated_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_reports",
    )
    metrics = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
