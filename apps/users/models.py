from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        COMPANY = "company", "Company"

    role = models.CharField(max_length=24, choices=Role.choices, default=Role.COMPANY)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    display_name = models.CharField(max_length=150, blank=True)

    @property
    def public_name(self) -> str:
        return self.display_name or (self.company.name if self.company_id else self.username)
