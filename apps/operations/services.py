from __future__ import annotations

from datetime import date, time, timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import DecimalField, F, QuerySet, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.commerce.models import Order
from apps.notifications.models import Notification
from apps.notifications.services import add_notification
from apps.operations.models import Conference, ConferenceAttendance, ManagementModule, Report
from apps.users.models import User
from core.utils import get_by_external

REPORT_PERIOD_DAYS = 30


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


def _revenue(orders: QuerySet[Order]) -> Decimal:
    """Sum quantity x unit price over the given orders.

    Product.price_amount is nullable, so each row is coalesced to 0 rather than
    poisoning the whole aggregate with NULL. Orders for products that carry only
    a display price_label and no numeric price_amount contribute nothing, which
    is why order_count is reported alongside revenue instead of being inferred
    from it.
    """
    total = orders.aggregate(
        total=Coalesce(
            Sum(
                F("quantity") * Coalesce(F("product__price_amount"), Decimal("0")),
                output_field=DecimalField(max_digits=18, decimal_places=2),
            ),
            Decimal("0"),
            output_field=DecimalField(max_digits=18, decimal_places=2),
        )
    )["total"]
    return total or Decimal("0")


def generate_report(user: User) -> Report:
    if not user.is_authenticated:
        raise PermissionDenied()
    scope = Report.Scope.ALL if user.role == User.Role.ADMIN else Report.Scope.COMPANY
    company = user.company if scope == Report.Scope.COMPANY else None

    orders = Order.objects.all() if scope == Report.Scope.ALL else Order.objects.filter(company=company)

    now = timezone.now()
    period_start = now - timedelta(days=REPORT_PERIOD_DAYS)
    previous_start = period_start - timedelta(days=REPORT_PERIOD_DAYS)

    current = orders.filter(created_at__gte=period_start)
    previous = orders.filter(created_at__gte=previous_start, created_at__lt=period_start)

    current_revenue = _revenue(current)
    previous_revenue = _revenue(previous)

    # Percentage change is undefined against a zero baseline, so report null
    # rather than inventing a figure the data cannot support.
    if previous_revenue > 0:
        change = (current_revenue - previous_revenue) / previous_revenue * 100
        growth = f"{change:+.1f}%"
    else:
        growth = None

    currencies = sorted(
        {
            currency
            for currency in current.values_list("product__currency", flat=True).distinct()
            if currency
        }
    )

    return Report.objects.create(
        scope=scope,
        company=company,
        generated_by=user,
        metrics={
            "periodDays": REPORT_PERIOD_DAYS,
            "orders": current.count(),
            "revenue": f"{current_revenue:.2f}",
            # A single total is only meaningful when one currency is involved;
            # surface the ambiguity instead of silently adding them together.
            "currency": currencies[0] if len(currencies) == 1 else ("MIXED" if currencies else None),
            "growth": growth,
            "totalOrders": orders.count(),
        },
    )
