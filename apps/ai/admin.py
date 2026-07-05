from django.contrib import admin

from .models import AiInteraction, AiUsage


@admin.register(AiUsage)
class AiUsageAdmin(admin.ModelAdmin):
    list_display = ("visitor_id", "prompt_count", "updated_at")
    search_fields = ("visitor_id",)


@admin.register(AiInteraction)
class AiInteractionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "visitor_id", "lang", "off_topic", "created_at")
    list_filter = ("lang", "off_topic")
