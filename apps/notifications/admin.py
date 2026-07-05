from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeDateTimeFilter, RelatedDropdownFilter

from .models import Notification, NotificationRead


class NotificationReadInline(TabularInline):
    model = NotificationRead
    extra = 0


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ("id", "audience", "target_company", "created_at")
    list_filter = (
        ("audience", ChoicesDropdownFilter),
        ("target_company", RelatedDropdownFilter),
        ("created_at", RangeDateTimeFilter),
    )
    search_fields = ("text", "link", "target_company__name")
    autocomplete_fields = ("target_company",)
    readonly_fields = ("created_at",)
    inlines = [NotificationReadInline]
    fieldsets = (
        (None, {"fields": ("audience", "target_company", "title_i18n", "text", "link")}),
        ("Metadata", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(NotificationRead)
class NotificationReadAdmin(ModelAdmin):
    list_display = ("id", "notification", "user", "read_at")
    list_filter = (
        ("notification", RelatedDropdownFilter),
        ("user", RelatedDropdownFilter),
        ("read_at", RangeDateTimeFilter),
    )
    search_fields = ("notification__text", "user__username", "user__email")
    autocomplete_fields = ("notification", "user")
    readonly_fields = ("read_at",)
