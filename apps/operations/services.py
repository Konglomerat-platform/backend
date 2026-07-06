from __future__ import annotations

from datetime import date, time

from django.db import transaction
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.notifications.models import Notification
from apps.notifications.services import add_notification
from apps.operations.models import Conference, ConferenceAttendance, ManagementModule, Report
from apps.users.models import User
from core.utils import get_by_external


def require_admin(user: User) -> None:
    if not user.is_authenticated or user.role != User.Role.ADMIN:
        raise PermissionDenied()


def normalize_conference_link(value: str) -> str:
    link = str(value or "").strip()
    if link and not link.startswith(("http://", "https://")):
        return f"https://{link}"
    return link


def parse_conference_date(value) -> date:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return date.today()


def parse_conference_time(value) -> time:
    if isinstance(value, time):
        return value
    try:
        return time.fromisoformat(str(value))
    except ValueError:
        return time(hour=12)


@transaction.atomic
def create_conference(user: User, payload: dict) -> Conference:
    require_admin(user)
    link = normalize_conference_link(payload.get("link") or "")
    item = Conference.objects.create(
        name=payload.get("name") or "Conference",
        date=parse_conference_date(payload.get("date") or date.today()),
        time=parse_conference_time(payload.get("time") or "12:00"),
        description=payload.get("desc") or payload.get("description") or "",
        link=link,
        capacity_total=int(payload.get("total") or 30),
    )
    add_notification(
        Notification.Audience.COMPANY,
        {"uz": "Yangi konferensiya", "ru": "Новая конференция", "en": "New conference"},
        f"{item.name} - {item.date} {item.time}",
        link or "/company",
    )
    return item


def join_conference(user: User, conference_id: str) -> Conference:
    conference = get_by_external(Conference, conference_id)
    if not conference:
        raise NotFound()
    if conference.attendances.count() < conference.capacity_total:
        ConferenceAttendance.objects.get_or_create(conference=conference, user=user)
    return conference


def delete_conference(user: User, conference_id: str) -> None:
    require_admin(user)
    conference = get_by_external(Conference, conference_id)
    if not conference:
        raise NotFound()
    conference.delete()


def update_module(user: User, key: str, enabled: bool) -> ManagementModule:
    require_admin(user)
    module, _ = ManagementModule.objects.get_or_create(
        key=key,
        defaults={"block_index": 0, "module_index": 0},
    )
    module.enabled = enabled
    module.save()
    return module


def generate_report(user: User) -> Report:
    if not user.is_authenticated:
        raise PermissionDenied()
    scope = Report.Scope.ALL if user.role == User.Role.ADMIN else Report.Scope.COMPANY
    company = user.company if scope == Report.Scope.COMPANY else None
    return Report.objects.create(
        scope=scope,
        company=company,
        generated_by=user,
        metrics={"revenue": "$48K", "orders": 186, "growth": "+22%"},
    )
