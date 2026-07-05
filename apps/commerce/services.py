from __future__ import annotations

from django.db import transaction
from rest_framework.exceptions import NotAuthenticated, NotFound, PermissionDenied, ValidationError

from apps.catalog.models import Product
from apps.commerce.models import FavoriteCollection, FavoriteItem, Order
from apps.notifications.models import Notification
from apps.notifications.services import add_notification
from apps.users.models import User
from core.utils import external_id, get_by_external


@transaction.atomic
def create_order(payload: dict) -> Order:
    product_id = payload.get("productId") or payload.get("product_id")
    product = get_by_external(Product, str(product_id))
    if not product:
        raise NotFound("product_not_found")
    name = str(payload.get("name", "")).strip()
    contact = str(payload.get("contact", "")).strip()
    if not name or not contact:
        raise ValidationError({"error": "missing_fields"})
    qty = max(1, int(payload.get("qty") or payload.get("quantity") or 1))
    order = Order.objects.create(
        product=product,
        company=product.company,
        product_snapshot={
            "name": product.name_i18n,
            "price": product.price_label,
            "company": product.company.name,
            "ico": product.icon,
        },
        customer_name=name,
        customer_contact=contact,
        quantity=qty,
    )
    product_name = product.name_i18n.get("ru") or product.name_i18n.get("en") or ""
    info = f'{name} - {contact} - "{product_name}"' + (f" x{qty}" if qty > 1 else "")
    add_notification(
        Notification.Audience.COMPANY,
        {"uz": "Yangi buyurtma", "ru": "Новая заявка на товар", "en": "New product request"},
        info,
        f"/company?order={external_id(order)}",
        product.company,
    )
    add_notification(
        Notification.Audience.ADMIN,
        {"uz": "Yangi buyurtma", "ru": "Новая заявка", "en": "New order"},
        f"{product.company.name}: {info}",
    )
    return order


def orders_for_user(user: User):
    if not user.is_authenticated:
        raise NotAuthenticated()
    qs = Order.objects.select_related("product", "company")
    if user.role == User.Role.COMPANY:
        return qs.filter(company=user.company)
    if user.role == User.Role.ADMIN:
        return qs
    raise PermissionDenied()


def favorite_ids_for_email(email: str) -> list[str]:
    email = email.strip().lower()
    if not email:
        raise ValidationError({"error": "email_required"})
    collection = FavoriteCollection.objects.filter(email=email).first()
    if not collection:
        return []
    return [external_id(item.product) for item in collection.items.select_related("product")]


@transaction.atomic
def replace_favorites(email: str, product_ids: list[str]) -> list[str]:
    email = email.strip().lower()
    if not email or "@" not in email:
        raise ValidationError({"error": "email_required"})
    collection, _ = FavoriteCollection.objects.get_or_create(email=email)
    collection.items.all().delete()
    saved = []
    for value in product_ids[:500]:
        product = get_by_external(Product, str(value))
        if product:
            FavoriteItem.objects.get_or_create(collection=collection, product=product)
            saved.append(external_id(product))
    return saved
