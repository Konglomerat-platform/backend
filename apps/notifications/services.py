from __future__ import annotations

from django.db.models import Q

from apps.companies.models import Company
from apps.notifications.models import Notification, NotificationRead
from apps.users.models import User


def add_notification(
    audience: str,
    title: dict,
    text: str,
    link: str = "",
    company: Company | None = None,
) -> Notification:
    return Notification.objects.create(
        audience=audience,
        title_i18n=title,
        text=text,
        link=link,
        target_company=company,
    )


def visible_notifications(user: User):
    qs = Notification.objects.filter(audience=user.role)
    if user.role == User.Role.COMPANY:
        qs = qs.filter(Q(target_company__isnull=True) | Q(target_company=user.company))
    return qs.order_by("-created_at", "-id")


def mark_all_read(user: User) -> None:
    for notification in visible_notifications(user):
        NotificationRead.objects.get_or_create(notification=notification, user=user)


def mark_notification_read(user: User, notification: Notification) -> None:
    NotificationRead.objects.get_or_create(notification=notification, user=user)
