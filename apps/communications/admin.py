from django.contrib import admin

from .models import ChatMessage, ChatThread, MessageReceipt


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0


@admin.register(ChatThread)
class ChatThreadAdmin(admin.ModelAdmin):
    list_display = ("id", "kind", "company", "title", "created_at")
    list_filter = ("kind", "company")
    inlines = [ChatMessageInline]


@admin.register(MessageReceipt)
class MessageReceiptAdmin(admin.ModelAdmin):
    list_display = ("message", "user", "seen_at")
