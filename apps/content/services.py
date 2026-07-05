from __future__ import annotations

from datetime import date

from django.db import transaction
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.companies.models import Company
from apps.content.models import NewsArticle, NewsImage
from apps.users.models import User
from core.utils import data_url_to_content, get_by_external, ml


def save_news_images(article: NewsArticle, image_values: list[str]) -> None:
    NewsImage.objects.filter(article=article).delete()
    for idx, value in enumerate(image_values[:3]):
        content = data_url_to_content(value, f"news-{article.id}-{idx + 1}")
        if content:
            NewsImage.objects.create(article=article, file=content, sort_order=idx)


def _require_admin(user: User) -> None:
    if not user.is_authenticated or user.role != User.Role.ADMIN:
        raise PermissionDenied()


@transaction.atomic
def create_news(user: User, payload: dict) -> NewsArticle:
    _require_admin(user)
    company = Company.objects.filter(name=payload.get("company")).first() if payload.get("company") else None
    content = ml(payload.get("content") or payload.get("body") or "")
    article = NewsArticle.objects.create(
        company=company,
        publisher_name=payload.get("company") or "Konglomerat",
        icon=payload.get("ico") or "",
        title_i18n=ml(payload.get("title")),
        summary_i18n=content,
        body_i18n={lang: [value] if value else [] for lang, value in content.items()},
        published_on=payload.get("date") or date.today(),
    )
    save_news_images(article, payload.get("images") or [])
    return article


@transaction.atomic
def update_news(user: User, article_id: str, payload: dict) -> NewsArticle:
    _require_admin(user)
    article = get_by_external(NewsArticle, article_id)
    if not article:
        raise NotFound()
    if "title" in payload:
        article.title_i18n = ml(payload.get("title"))
    if "content" in payload or "body" in payload:
        content = ml(payload.get("content") or payload.get("body"))
        article.summary_i18n = content
        article.body_i18n = {lang: [value] if value else [] for lang, value in content.items()}
    if "date" in payload:
        article.published_on = payload.get("date")
    if "ico" in payload:
        article.icon = payload.get("ico") or ""
    article.save()
    if "images" in payload:
        save_news_images(article, payload.get("images") or [])
    return article


def delete_news(user: User, article_id: str) -> None:
    _require_admin(user)
    article = get_by_external(NewsArticle, article_id)
    if not article:
        raise NotFound()
    article.delete()
