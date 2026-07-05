from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter, FieldTextFilter, RangeDateTimeFilter, RelatedDropdownFilter

from .models import AiInteraction, AiUsage


@admin.register(AiUsage)
class AiUsageAdmin(ModelAdmin):
    list_display = ("visitor_id", "prompt_count", "updated_at")
    search_fields = ("visitor_id",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(AiInteraction)
class AiInteractionAdmin(ModelAdmin):
    list_display = ("id", "user", "visitor_id", "lang", "off_topic", "created_at")
    list_filter = (
        ("lang", FieldTextFilter),
        ("off_topic", ChoicesDropdownFilter),
        ("user", RelatedDropdownFilter),
        ("created_at", RangeDateTimeFilter),
    )
    search_fields = ("visitor_id", "prompt", "reply", "user__username", "user__email")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at",)
