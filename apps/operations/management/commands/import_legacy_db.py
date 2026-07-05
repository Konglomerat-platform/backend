from __future__ import annotations

import json
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.catalog.models import Product
from apps.commerce.models import FavoriteCollection, FavoriteItem, Order
from apps.companies.models import Company
from apps.content.models import NewsArticle
from apps.innovation.models import RndSubmission
from apps.operations.models import Conference, ManagementModule
from apps.support.models import Complaint


class Command(BaseCommand):
    help = "Import the legacy Node db.json into the normalized Django schema."

    def add_arguments(self, parser):
        parser.add_argument("--source", required=True, help="Path to legacy data/db.json")

    @transaction.atomic
    def handle(self, *args, **options):
        source = Path(options["source"])
        if not source.exists():
            raise CommandError(f"Legacy DB not found: {source}")
        data = json.loads(source.read_text(encoding="utf-8"))
        call_command("seed_demo_data")

        companies = {c.name: c for c in Company.objects.all()}

        def company_for(name: str) -> Company:
            if name not in companies:
                companies[name], _ = Company.objects.get_or_create(name=name, defaults={"slug": slugify(name)})
            return companies[name]

        for item in data.get("products", []):
            Product.objects.update_or_create(
                legacy_id=item.get("id"),
                defaults={
                    "company": company_for(item.get("company") or "Konglomerat"),
                    "icon": item.get("ico") or "",
                    "name_i18n": item.get("name") or {},
                    "description_i18n": item.get("desc") or {},
                    "price_label": item.get("price") or "",
                },
            )

        for item in data.get("news", []):
            company = company_for(item.get("company") or "Konglomerat")
            NewsArticle.objects.update_or_create(
                legacy_id=item.get("id"),
                defaults={
                    "company": company,
                    "publisher_name": company.name,
                    "icon": item.get("ico") or "",
                    "title_i18n": item.get("title") or {},
                    "summary_i18n": item.get("text") or {},
                    "body_i18n": item.get("body") or {},
                    "published_on": item.get("date") or "2026-01-01",
                },
            )

        for item in data.get("conferences", []):
            Conference.objects.update_or_create(
                legacy_id=item.get("id"),
                defaults={
                    "name": item.get("name") or "Conference",
                    "date": item.get("date") or "2026-01-01",
                    "time": item.get("time") or "12:00",
                    "capacity_total": item.get("total") or 30,
                    "link": item.get("link") or "",
                    "description": item.get("desc") or "",
                },
            )

        for item in data.get("complaints", []):
            from_name = item.get("from") or "-"
            Complaint.objects.update_or_create(
                legacy_id=item.get("id"),
                defaults={
                    "from_company": companies.get(from_name),
                    "from_name": from_name,
                    "contact": item.get("contact") or "",
                    "subject_i18n": item.get("title") if isinstance(item.get("title"), dict) else {},
                    "message_i18n": item.get("text") if isinstance(item.get("text"), dict) else {},
                    "raw_message": item.get("text") if isinstance(item.get("text"), str) else "",
                    "official": bool(item.get("official")),
                    "reply": item.get("reply") or "",
                    "status": item.get("status") or "pending",
                },
            )

        for item in data.get("rnd", []):
            RndSubmission.objects.update_or_create(
                legacy_id=item.get("id"),
                defaults={
                    "company": company_for(item.get("company") or "Konglomerat"),
                    "category": item.get("cat") or "-",
                    "name_i18n": item.get("name") or {},
                    "description_i18n": item.get("desc") or {},
                    "patent_requested": bool(item.get("patent")),
                    "status": item.get("status") or "pending",
                },
            )

        for key, enabled in (data.get("modules") or {}).items():
            _, block, module = (key.split("-") + ["0", "0"])[:3]
            ManagementModule.objects.update_or_create(
                key=key,
                defaults={"block_index": int(block), "module_index": int(module), "enabled": bool(enabled)},
            )

        for email, product_ids in (data.get("favorites") or {}).items():
            collection, _ = FavoriteCollection.objects.get_or_create(email=email)
            collection.items.all().delete()
            for legacy_id in product_ids:
                product = Product.objects.filter(legacy_id=legacy_id).first()
                if product:
                    FavoriteItem.objects.get_or_create(collection=collection, product=product)

        for item in data.get("orders", []):
            product = Product.objects.filter(legacy_id=item.get("productId")).first()
            if product:
                Order.objects.update_or_create(
                    legacy_id=item.get("id"),
                    defaults={
                        "product": product,
                        "company": product.company,
                        "product_snapshot": item.get("product") or {},
                        "customer_name": (item.get("customer") or {}).get("name") or "",
                        "customer_contact": (item.get("customer") or {}).get("contact") or "",
                        "quantity": item.get("qty") or 1,
                        "status": item.get("status") or "new",
                    },
                )

        self.stdout.write(self.style.SUCCESS(f"Imported legacy DB from {source}"))
