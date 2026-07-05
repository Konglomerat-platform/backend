from django.db import models


class Product(models.Model):
    legacy_id = models.CharField(max_length=40, blank=True, unique=True, null=True)
    company = models.ForeignKey("companies.Company", on_delete=models.PROTECT, related_name="products")
    icon = models.CharField(max_length=24, blank=True)
    name_i18n = models.JSONField(default=dict)
    description_i18n = models.JSONField(default=dict, blank=True)
    price_label = models.CharField(max_length=80, blank=True)
    price_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=12, blank=True, default="USD")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["company", "-created_at"]),
        ]

    def __str__(self) -> str:
        return self.name_i18n.get("en") or self.name_i18n.get("ru") or f"Product {self.pk}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    file = models.FileField(upload_to="products/")
    sort_order = models.PositiveSmallIntegerField(default=0)
    name = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["sort_order", "id"]
