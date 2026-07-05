from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeDateTimeFilter, RelatedDropdownFilter

from .models import Complaint, ComplaintAttachment


class ComplaintAttachmentInline(TabularInline):
    model = ComplaintAttachment
    extra = 0


@admin.register(Complaint)
class ComplaintAdmin(ModelAdmin):
    list_display = ("id", "legacy_id", "from_name", "status", "official", "created_at")
    list_filter = (
        ("status", ChoicesDropdownFilter),
        ("official", ChoicesDropdownFilter),
        ("from_company", RelatedDropdownFilter),
        ("created_at", RangeDateTimeFilter),
    )
    search_fields = ("legacy_id", "from_name", "contact", "raw_message")
    autocomplete_fields = ("from_company",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [ComplaintAttachmentInline]
    fieldsets = (
        (None, {"fields": ("legacy_id", "from_company", "from_name", "contact", "official", "status")}),
        ("Message", {"fields": ("subject_i18n", "message_i18n", "raw_message", "reply")}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(ComplaintAttachment)
class ComplaintAttachmentAdmin(ModelAdmin):
    list_display = ("id", "complaint", "kind", "name", "duration_seconds", "created_at")
    list_filter = (("kind", ChoicesDropdownFilter), ("created_at", RangeDateTimeFilter))
    search_fields = ("name", "complaint__legacy_id", "complaint__from_name")
    autocomplete_fields = ("complaint",)
    readonly_fields = ("created_at",)
