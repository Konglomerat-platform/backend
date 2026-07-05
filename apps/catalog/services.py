from __future__ import annotations

from django.db import transaction
from django.utils.text import slugify
from rest_framework.exceptions import NotAuthenticated, NotFound, PermissionDenied, ValidationError

from apps.catalog.models import Product, ProductImage
from apps.companies.models import Company
from apps.users.models import User
from core.utils import data_url_to_content, get_by_external, ml, parse_decimal_label


def save_product_images(product: Product, image_values: list[str]) -> None:
    ProductImage.objects.filter(product=product).delete()
    for idx, value in enumerate(image_values[:3]):
        content = data_url_to_content(value, f"product-{product.id}-{idx + 1}")
        if content:
            ProductImage.objects.create(product=product, file=content, sort_order=idx)


def _company_for_request(user: User, company_name: str | None) -> Company:
    if user.role == User.Role.COMPANY:
        if not user.company_id:
            raise ValidationError({"company": "company_required"})
        return user.company

    name = company_name or "Konglomerat"
    company, _ = Company.objects.get_or_create(name=name, defaults={"slug": slugify(name)})
    return company


@transaction.atomic
def create_product(user: User, payload: dict) -> Product:
    if not user.is_authenticated:
        raise NotAuthenticated()
    if user.role not in {User.Role.ADMIN, User.Role.COMPANY}:
        raise PermissionDenied()
    company = _company_for_request(user, payload.get("company"))
    product = Product.objects.create(
        company=company,
        icon=payload.get("ico") or payload.get("icon") or "",
        name_i18n=ml(payload.get("name")),
        description_i18n=ml(payload.get("desc") or payload.get("description")),
        price_label=str(payload.get("price") or ""),
        price_amount=parse_decimal_label(str(payload.get("price") or "")),
    )
    save_product_images(product, payload.get("images") or [])
    return product


@transaction.atomic
def update_product(user: User, product_id: str, payload: dict) -> Product:
    if not user.is_authenticated:
        raise NotAuthenticated()
    product = get_by_external(Product, product_id)
    if not product:
        raise NotFound()
    if user.role != User.Role.ADMIN and product.company_id != user.company_id:
        raise PermissionDenied()
    if "name" in payload:
        product.name_i18n = ml(payload.get("name"))
    if "desc" in payload or "description" in payload:
        product.description_i18n = ml(payload.get("desc") or payload.get("description"))
    if "price" in payload:
        product.price_label = str(payload.get("price") or "")
        product.price_amount = parse_decimal_label(product.price_label)
    if "ico" in payload or "icon" in payload:
        product.icon = payload.get("ico") or payload.get("icon") or ""
    product.save()
    if "images" in payload:
        save_product_images(product, payload.get("images") or [])
    return product


def delete_product(user: User, product_id: str) -> None:
    if not user.is_authenticated:
        raise NotAuthenticated()
    product = get_by_external(Product, product_id)
    if not product:
        raise NotFound()
    if user.role != User.Role.ADMIN and product.company_id != user.company_id:
        raise PermissionDenied()
    product.delete()
