from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeDateTimeFilter, RelatedDropdownFilter

from .models import ChatAttachment, ChatMessage, ChatThread, MessageReceipt


class ChatMessageInline(TabularInline):
    model = ChatMessage
    extra = 0


class ChatAttachmentInline(TabularInline):
    model = ChatAttachment
    extra = 0


@admin.register(ChatThread)
class ChatThreadAdmin(ModelAdmin):
    list_display = ("id", "kind", "company", "title", "created_at")
    list_filter = (
        ("kind", ChoicesDropdownFilter),
        ("company", RelatedDropdownFilter),
        ("created_at", RangeDateTimeFilter),
    )
    search_fields = ("title", "company__name")
    autocomplete_fields = ("company",)
    readonly_fields = ("created_at",)
    inlines = [ChatMessageInline]


@admin.register(ChatMessage)
class ChatMessageAdmin(ModelAdmin):
    list_display = ("id", "thread", "sender", "kind", "edited", "created_at")
    list_filter = (
        ("kind", ChoicesDropdownFilter),
        ("edited", ChoicesDropdownFilter),
        ("thread", RelatedDropdownFilter),
        ("sender", RelatedDropdownFilter),
        ("created_at", RangeDateTimeFilter),
    )
    search_fields = ("legacy_id", "text", "name", "sender__username", "sender__email")
    autocomplete_fields = ("thread", "sender")
    readonly_fields = ("created_at", "updated_at")
    inlines = [ChatAttachmentInline]


@admin.register(ChatAttachment)
class ChatAttachmentAdmin(ModelAdmin):
    list_display = ("id", "message", "kind", "name", "content_type", "size_bytes", "sort_order")
    list_filter = (
        ("kind", ChoicesDropdownFilter),
        ("message", RelatedDropdownFilter),
    )
    search_fields = ("name", "message__text")
    autocomplete_fields = ("message",)
    readonly_fields = ("created_at",)


@admin.register(MessageReceipt)
class MessageReceiptAdmin(ModelAdmin):
    list_display = ("message", "user", "seen_at")
    list_filter = (
        ("user", RelatedDropdownFilter),
        ("seen_at", RangeDateTimeFilter),
    )
    search_fields = ("message__text", "user__username", "user__email")
    autocomplete_fields = ("message", "user")
    readonly_fields = ("seen_at",)
