from django.db import models


class NewsArticle(models.Model):
    legacy_id = models.CharField(max_length=40, blank=True, unique=True, null=True)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="news_articles",
    )
    publisher_name = models.CharField(max_length=160, blank=True)
    icon = models.CharField(max_length=24, blank=True)
    title_i18n = models.JSONField(default=dict)
    summary_i18n = models.JSONField(default=dict, blank=True)
    body_i18n = models.JSONField(default=dict, blank=True)
    published_on = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_on", "-created_at"]

    def __str__(self) -> str:
        return self.title_i18n.get("en") or self.title_i18n.get("ru") or f"News {self.pk}"


class NewsImage(models.Model):
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name="images")
    file = models.FileField(upload_to="news/")
    sort_order = models.PositiveSmallIntegerField(default=0)
    name = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["sort_order", "id"]
