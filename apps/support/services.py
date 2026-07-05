from __future__ import annotations

from django.db import transaction
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.notifications.models import Notification
from apps.notifications.services import add_notification
from apps.support.models import Complaint, ComplaintAttachment
from apps.users.models import User
from apps.users.permissions import is_company
from core.utils import data_url_to_content, external_id, get_by_external, ml


def _require_admin(user: User) -> None:
    if not user.is_authenticated or user.role != User.Role.ADMIN:
        raise PermissionDenied()


@transaction.atomic
def create_complaint(user: User, payload: dict) -> Complaint:
    from_company = user.company if is_company(user) else None
    from_name = from_company.name if from_company else str(payload.get("name") or "").strip() or "-"
    text = payload.get("text") or payload.get("message") or ""
    raw = text if isinstance(text, str) else ""
    if not raw and not text:
        raise ValidationError({"error": "empty"})

    complaint = Complaint.objects.create(
        from_company=from_company,
        from_name=from_name,
        contact=str(payload.get("contact") or "").strip(),
        subject_i18n=ml(payload.get("title")) if payload.get("title") else {},
        message_i18n=ml(text) if isinstance(text, dict) else {},
        raw_message=raw,
        official=bool(payload.get("official")),
    )

    for idx, value in enumerate(payload.get("images") or []):
        content = data_url_to_content(value, f"complaint-{complaint.id}-image-{idx + 1}")
        if content:
            ComplaintAttachment.objects.create(
                complaint=complaint,
                kind=ComplaintAttachment.Kind.IMAGE,
                file=content,
            )

    for idx, attachment in enumerate(payload.get("attachments") or []):
        content = data_url_to_content(attachment.get("data"), f"complaint-{complaint.id}-att-{idx + 1}")
        if content:
            kind = attachment.get("kind") if attachment.get("kind") in {"image", "file", "voice"} else "file"
            ComplaintAttachment.objects.create(
                complaint=complaint,
                kind=kind,
                file=content,
                name=str(attachment.get("name") or "")[:200],
                duration_seconds=attachment.get("dur") or None,
            )

    preview = payload.get("title") or raw or str(text)
    add_notification(
        Notification.Audience.ADMIN,
        {"uz": "Yangi shikoyat", "ru": "Новая жалоба", "en": "New complaint"},
        f"{from_name}: {str(preview)[:80]}",
        f"/admin/complaints/{external_id(complaint)}",
    )
    return complaint


def update_complaint(user: User, complaint_id: str, payload: dict) -> Complaint:
    _require_admin(user)
    complaint = get_by_external(Complaint, complaint_id)
    if not complaint:
        raise NotFound()
    if "reply" in payload:
        complaint.reply = str(payload.get("reply") or "")
    if payload.get("status") in {Complaint.Status.PENDING, Complaint.Status.RESOLVED}:
        complaint.status = payload["status"]
    complaint.save()
    return complaint


def delete_complaint(user: User, complaint_id: str) -> None:
    _require_admin(user)
    complaint = get_by_external(Complaint, complaint_id)
    if not complaint:
        raise NotFound()
    complaint.delete()
