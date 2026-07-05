from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "sector", "active", "created_at")
    list_filter = ("active", "sector")
    search_fields = ("name", "slug", "email", "phone")
    prepopulated_fields = {"slug": ("name",)}
