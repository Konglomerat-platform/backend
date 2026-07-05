from __future__ import annotations

from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.companies.models import Company
from apps.innovation.models import RndSubmission
from apps.users.models import User
from core.utils import get_by_external, ml


def submissions_for_user(user: User, company_name: str | None = None):
    qs = RndSubmission.objects.select_related("company")
    if user.role == User.Role.COMPANY:
        return qs.filter(company=user.company)
    if company_name:
        return qs.filter(company__name=company_name)
    return qs


def create_submission(user: User, payload: dict) -> RndSubmission:
    if user.role == User.Role.COMPANY:
        company = user.company
    elif user.role == User.Role.ADMIN and payload.get("company"):
        company = Company.objects.get(name=payload["company"])
    else:
        raise PermissionDenied()
    return RndSubmission.objects.create(
        company=company,
        category=payload.get("cat") or payload.get("category") or "-",
        name_i18n=ml(payload.get("name")),
        description_i18n=ml(payload.get("desc") or payload.get("description")),
        patent_requested=bool(payload.get("patent")),
    )


def update_submission(user: User, submission_id: str, payload: dict) -> RndSubmission:
    if user.role != User.Role.ADMIN:
        raise PermissionDenied()
    item = get_by_external(RndSubmission, submission_id)
    if not item:
        raise NotFound()
    if payload.get("status") in {
        RndSubmission.Status.PENDING,
        RndSubmission.Status.APPROVED,
        RndSubmission.Status.REJECTED,
    }:
        item.status = payload["status"]
        item.reviewed_by = user
        item.reviewed_at = timezone.now()
        item.save()
    return item
