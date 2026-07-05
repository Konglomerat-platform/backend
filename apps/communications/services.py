from __future__ import annotations

from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.communications.models import ChatMessage, ChatThread, MessageReceipt
from apps.companies.models import Company
from apps.users.models import User
from core.utils import data_url_to_content, get_by_external


def thread_for_chat(chat: str, user: User) -> ChatThread | None:
    if chat == "group":
        thread, _ = ChatThread.objects.get_or_create(
            kind=ChatThread.Kind.GROUP,
            company=None,
            defaults={"title": "Group chat"},
        )
        return thread
    company = Company.objects.filter(name=chat).first()
    if not company:
        return None
    if user.role != User.Role.ADMIN and user.company_id != company.id:
        return None
    thread, _ = ChatThread.objects.get_or_create(
        kind=ChatThread.Kind.ADMIN_COMPANY,
        company=company,
        defaults={"title": f"Admin - {company.name}"},
    )
    return thread


def messages_for_chat(chat: str, user: User):
    thread = thread_for_chat(chat, user)
    if not thread:
        raise PermissionDenied()
    return thread.messages.select_related("sender", "thread__company").prefetch_related("receipts__user")


def create_message(user: User, payload: dict) -> ChatMessage:
    thread = thread_for_chat(payload.get("chat") or "", user)
    if not thread:
        raise PermissionDenied()
    kind = payload.get("kind") if payload.get("kind") in {"text", "image", "file", "voice"} else "text"
    message = ChatMessage.objects.create(
        thread=thread,
        sender=user,
        kind=kind,
        text=str(payload.get("text") or ""),
        name=str(payload.get("name") or "")[:200],
        duration_seconds=payload.get("dur") or None,
    )
    if kind != ChatMessage.Kind.TEXT:
        content = data_url_to_content(payload.get("data"), f"message-{message.id}")
        if not content:
            message.delete()
            raise ValidationError({"error": "no_data"})
        message.file.save(content.name, content, save=True)
    return message


def mark_seen(user: User, chat: str) -> None:
    thread = thread_for_chat(chat, user)
    if not thread:
        raise PermissionDenied()
    for message in thread.messages.exclude(sender=user):
        MessageReceipt.objects.get_or_create(message=message, user=user)


def update_message(user: User, message_id: str, payload: dict) -> ChatMessage:
    message = get_by_external(ChatMessage, message_id)
    if not message:
        raise NotFound()
    if message.sender_id != user.id:
        raise PermissionDenied()
    if message.kind != ChatMessage.Kind.TEXT:
        raise ValidationError({"error": "not_text"})
    text = str(payload.get("text") or "").strip()
    if not text:
        raise ValidationError({"error": "empty"})
    message.text = text
    message.edited = True
    message.save()
    return message


def delete_message(user: User, message_id: str) -> None:
    message = get_by_external(ChatMessage, message_id)
    if not message:
        raise NotFound()
    if message.sender_id != user.id and user.role != User.Role.ADMIN:
        raise PermissionDenied()
    message.delete()
