from django.contrib import admin

from .models import Complaint, ComplaintAttachment


class ComplaintAttachmentInline(admin.TabularInline):
    model = ComplaintAttachment
    extra = 0


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "from_name", "status", "official", "created_at")
    list_filter = ("status", "official")
    search_fields = ("legacy_id", "from_name", "contact", "raw_message")
    inlines = [ComplaintAttachmentInline]
