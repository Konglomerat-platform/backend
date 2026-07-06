from __future__ import annotations

import mimetypes
from pathlib import PurePath
from uuid import uuid4

from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.communications.models import ChatMessage, ChatThread, MessageReceipt
from apps.companies.models import Company
from apps.users.models import User
from core.utils import data_url_to_content, get_by_external

VALID_KINDS = {
    ChatMessage.Kind.TEXT,
    ChatMessage.Kind.IMAGE,
    ChatMessage.Kind.FILE,
    ChatMessage.Kind.VIDEO,
    ChatMessage.Kind.VOICE,
}


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


def user_can_access_thread(user: User, thread: ChatThread) -> bool:
    if not user or not user.is_authenticated:
        return False
    if thread.kind == ChatThread.Kind.GROUP:
        return True
    return user.role == User.Role.ADMIN or user.company_id == thread.company_id


def messages_for_chat(chat: str, user: User):
    thread = thread_for_chat(chat, user)
    if not thread:
        raise PermissionDenied()
    return (
        thread.messages.select_related("sender", "thread__company", "parent__sender")
        .prefetch_related("receipts__user")
    )


def message_for_user(user: User, message_id: str) -> ChatMessage:
    message = get_by_external(ChatMessage, message_id)
    if not message:
        raise NotFound()
    if not user_can_access_thread(user, message.thread):
        raise PermissionDenied()
    return _message_queryset().get(pk=message.pk)


def _message_queryset():
    return ChatMessage.objects.select_related("sender", "thread__company", "parent__sender").prefetch_related(
        "receipts__user"
    )


def _clean_filename(value: str) -> str:
    name = PurePath(value or "").name.strip()
    return name[:255] or "attachment"


def _storage_filename(message_id: int, original_name: str, content_type: str = "") -> str:
    suffix = PurePath(original_name or "").suffix
    if not suffix and content_type:
        suffix = mimetypes.guess_extension(content_type.split(";", 1)[0].strip()) or ""
    suffix = suffix[:20] if suffix else ".bin"
    return f"message-{message_id}-{uuid4().hex[:8]}{suffix.lower()}"


def _kind_from_file(file_obj, fallback: str) -> str:
    content_type = getattr(file_obj, "content_type", "") or ""
    if content_type.startswith("image/"):
        return ChatMessage.Kind.IMAGE
    if content_type.startswith("video/"):
        return ChatMessage.Kind.VIDEO
    if content_type.startswith("audio/") and fallback == ChatMessage.Kind.VOICE:
        return ChatMessage.Kind.VOICE
    return fallback if fallback != ChatMessage.Kind.TEXT else ChatMessage.Kind.FILE


def create_message(user: User, payload: dict) -> ChatMessage:
    thread = thread_for_chat(payload.get("chat") or "", user)
    if not thread:
        raise PermissionDenied()
    upload = payload.get("file")
    requested_kind = payload.get("kind") if payload.get("kind") in VALID_KINDS else ChatMessage.Kind.TEXT
    kind = _kind_from_file(upload, requested_kind) if upload else requested_kind
    parent = None
    parent_id = payload.get("parent") or payload.get("parentId")
    if parent_id:
        parent = get_by_external(ChatMessage, str(parent_id), thread=thread)
        if not parent:
            raise ValidationError({"parent": "invalid"})
    raw_name = str(payload.get("name") or getattr(upload, "name", "") or "")
    message = ChatMessage.objects.create(
        thread=thread,
        parent=parent,
        sender=user,
        kind=kind,
        text=str(payload.get("text") or ""),
        name=_clean_filename(raw_name) if raw_name else "",
        content_type=str(payload.get("contentType") or getattr(upload, "content_type", "") or "")[:127],
        size_bytes=getattr(upload, "size", None) or None,
        duration_seconds=payload.get("dur") or None,
    )
    if upload:
        message.file.save(
            _storage_filename(message.id, message.name, message.content_type),
            upload,
            save=False,
        )
        message.save()
    elif kind != ChatMessage.Kind.TEXT:
        content = data_url_to_content(payload.get("data"), f"message-{message.id}")
        if not content:
            message.delete()
            raise ValidationError({"error": "no_data"})
        message.file.save(content.name, content, save=False)
        message.size_bytes = content.size
        message.save()
    return _message_queryset().get(pk=message.pk)


def mark_seen(user: User, chat: str) -> list[ChatMessage]:
    thread = thread_for_chat(chat, user)
    if not thread:
        raise PermissionDenied()
    changed_ids = []
    for message in thread.messages.exclude(sender=user):
        _, created = MessageReceipt.objects.get_or_create(message=message, user=user)
        if created:
            changed_ids.append(message.id)
    if not changed_ids:
        return []
    return list(_message_queryset().filter(id__in=changed_ids))


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
    return _message_queryset().get(pk=message.pk)


def delete_message(user: User, message_id: str) -> ChatMessage:
    message = get_by_external(ChatMessage, message_id)
    if not message:
        raise NotFound()
    if message.sender_id != user.id and user.role != User.Role.ADMIN:
        raise PermissionDenied()
    deleted = message
    message.delete()
    return deleted
