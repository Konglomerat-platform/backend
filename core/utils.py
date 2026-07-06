from __future__ import annotations

import base64
import binascii
import re
from decimal import Decimal, InvalidOperation
from typing import Any

from django.conf import settings
from django.core.files.base import ContentFile


def external_id(obj: Any) -> str:
    legacy_id = getattr(obj, "legacy_id", None)
    return legacy_id or str(obj.id)


def get_by_external(model, value: str, **filters):
    qs = model.objects.filter(**filters)
    found = qs.filter(legacy_id=value).first()
    if found:
        return found
    if str(value).isdigit():
        return qs.filter(pk=int(value)).first()
    return None


def localized_file_url(request, file_field) -> str | None:
    if not file_field:
        return None
    try:
        url = request.build_absolute_uri(file_field.url)
    except ValueError:
        return None
    if getattr(settings, "APP_FORCE_HTTPS", False) and url.startswith("http://"):
        return "https://" + url.removeprefix("http://")
    return url


def loc(value: dict | str | None, lang: str = "ru") -> str:
    if isinstance(value, dict):
        return value.get(lang) or value.get("ru") or value.get("en") or value.get("uz") or ""
    return "" if value is None else str(value)


def ml(value: dict | str | None) -> dict[str, str]:
    if isinstance(value, dict):
        first = next((str(value.get(k, "")).strip() for k in ("uz", "ru", "en") if value.get(k)), "")
        return {k: str(value.get(k, "")).strip() or first for k in ("uz", "ru", "en")}
    text = "" if value is None else str(value).strip()
    return {"uz": text, "ru": text, "en": text}


def parse_decimal_label(label: str) -> Decimal | None:
    cleaned = re.sub(r"[^\d.]", "", label or "")
    if not cleaned:
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def data_url_to_content(data_url: str, prefix: str) -> ContentFile | None:
    if not isinstance(data_url, str) or not data_url.startswith("data:") or "," not in data_url:
        return None
    meta, encoded = data_url.split(",", 1)
    ext = "bin"
    if "/" in meta:
        ext = meta.split("/", 1)[1].split(";", 1)[0].replace("+xml", "")
    try:
        raw = base64.b64decode(encoded)
    except (binascii.Error, ValueError):
        return None
    return ContentFile(raw, name=f"{prefix}.{ext}")
