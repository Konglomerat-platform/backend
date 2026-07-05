from django.db import models


class AiUsage(models.Model):
    visitor_id = models.CharField(max_length=180, unique=True)
    prompt_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AiInteraction(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_interactions",
    )
    visitor_id = models.CharField(max_length=180, blank=True)
    prompt = models.TextField()
    reply = models.TextField(blank=True)
    lang = models.CharField(max_length=8, default="ru")
    off_topic = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
