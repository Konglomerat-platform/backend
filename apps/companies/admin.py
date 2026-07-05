from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter, FieldTextFilter

from .models import Company


@admin.register(Company)
class CompanyAdmin(ModelAdmin):
    list_display = ("name", "sector", "active", "created_at")
    list_filter = (("active", ChoicesDropdownFilter), ("sector", FieldTextFilter))
    search_fields = ("name", "slug", "email", "phone")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "slug", "sector", "active")}),
        ("Contacts", {"fields": ("email", "phone")}),
        ("Data", {"fields": ("metadata",), "classes": ("collapse",)}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
