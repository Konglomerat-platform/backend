from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    ChoicesDropdownFilter,
    FieldTextFilter,
    RangeDateFilter,
    RangeDateTimeFilter,
    RelatedDropdownFilter,
)

from .models import Conference, ConferenceAttendance, ManagementModule, Report


class ConferenceAttendanceInline(TabularInline):
    model = ConferenceAttendance
    extra = 0


@admin.register(Conference)
class ConferenceAdmin(ModelAdmin):
    list_display = ("id", "legacy_id", "name", "date", "time", "capacity_total")
    list_filter = (("date", RangeDateFilter), ("created_at", RangeDateTimeFilter))
    search_fields = ("legacy_id", "name")
    readonly_fields = ("created_at",)
    inlines = [ConferenceAttendanceInline]
    fieldsets = (
        (None, {"fields": ("legacy_id", "name", "date", "time", "capacity_total")}),
        ("Details", {"fields": ("description", "link")}),
        ("Metadata", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(ConferenceAttendance)
class ConferenceAttendanceAdmin(ModelAdmin):
    list_display = ("id", "conference", "user", "joined_at")
    list_filter = (
        ("conference", RelatedDropdownFilter),
        ("user", RelatedDropdownFilter),
        ("joined_at", RangeDateTimeFilter),
    )
    search_fields = ("conference__name", "user__username", "user__email")
    autocomplete_fields = ("conference", "user")
    readonly_fields = ("joined_at",)


@admin.register(ManagementModule)
class ManagementModuleAdmin(ModelAdmin):
    list_display = ("key", "block_index", "module_index", "enabled", "updated_at")
    list_filter = (("enabled", ChoicesDropdownFilter), ("block_index", FieldTextFilter))
    search_fields = ("key",)
    readonly_fields = ("updated_at",)


@admin.register(Report)
class ReportAdmin(ModelAdmin):
    list_display = ("id", "scope", "company", "generated_by", "created_at")
    list_filter = (
        ("scope", ChoicesDropdownFilter),
        ("company", RelatedDropdownFilter),
        ("generated_by", RelatedDropdownFilter),
        ("created_at", RangeDateTimeFilter),
    )
    search_fields = ("company__name", "generated_by__username", "generated_by__email")
    autocomplete_fields = ("company", "generated_by")
    readonly_fields = ("created_at",)
