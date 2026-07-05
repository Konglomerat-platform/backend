from django.contrib import admin

from .models import RndSubmission


@admin.register(RndSubmission)
class RndSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "company", "category", "status", "patent_requested", "created_at")
    list_filter = ("status", "patent_requested", "company")
    search_fields = ("legacy_id", "category", "company__name")
