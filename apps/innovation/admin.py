from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeDateTimeFilter, RelatedDropdownFilter

from .models import RndSubmission


@admin.register(RndSubmission)
class RndSubmissionAdmin(ModelAdmin):
    list_display = ("id", "legacy_id", "company", "category", "status", "patent_requested", "created_at")
    list_filter = (
        ("status", ChoicesDropdownFilter),
        ("patent_requested", ChoicesDropdownFilter),
        ("company", RelatedDropdownFilter),
        ("reviewed_by", RelatedDropdownFilter),
        ("created_at", RangeDateTimeFilter),
    )
    search_fields = ("legacy_id", "category", "company__name")
    autocomplete_fields = ("company", "reviewed_by")
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("legacy_id", "company", "category", "status", "patent_requested")}),
        ("Content", {"fields": ("name_i18n", "description_i18n")}),
        ("Review", {"fields": ("reviewed_by", "reviewed_at")}),
        ("Metadata", {"fields": ("created_at",), "classes": ("collapse",)}),
    )
