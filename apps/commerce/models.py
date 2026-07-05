from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        CLOSED = "closed", "Closed"

    legacy_id = models.CharField(max_length=40, blank=True, unique=True, null=True)
    product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT, related_name="orders")
    company = models.ForeignKey("companies.Company", on_delete=models.PROTECT, related_name="orders")
    product_snapshot = models.JSONField(default=dict)
    customer_name = models.CharField(max_length=180)
    customer_contact = models.CharField(max_length=180)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["company", "status", "-created_at"])]


class FavoriteCollection(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["email"]


class FavoriteItem(models.Model):
    collection = models.ForeignKey(FavoriteCollection, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="favorite_items")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["collection", "product"], name="unique_favorite_product")
        ]
