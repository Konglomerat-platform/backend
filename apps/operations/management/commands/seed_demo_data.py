from __future__ import annotations

from datetime import date, time

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.catalog.models import Product
from apps.communications.models import ChatMessage, ChatThread
from apps.companies.models import Company
from apps.content.models import NewsArticle
from apps.innovation.models import RndSubmission
from apps.operations.models import Conference, ManagementModule
from apps.support.models import Complaint
from apps.users.models import User


def tr(uz: str, ru: str, en: str) -> dict[str, str]:
    return {"uz": uz, "ru": ru, "en": en}


class Command(BaseCommand):
    help = "Seed demo Konglomerat data matching the legacy business flow."

    @transaction.atomic
    def handle(self, *args, **options):
        companies = {
            name: Company.objects.get_or_create(
                name=name,
                defaults={"slug": slugify(name), "sector": sector},
            )[0]
            for name, sector in [
                ("Oltin Saroy", "Jewelry"),
                ("Mebel Pro", "Furniture"),
                ("Vaqt Lux", "Watches"),
                ("Charm House", "Leather"),
                ("Hunarmand", "Crafts"),
                ("Atlas Silk", "Textile"),
                ("TechNation", "Technology"),
                ("Asal Bio", "Food"),
                ("Konglomerat", "Platform"),
            ]
        }

        admin, _ = User.objects.update_or_create(
            username="admin",
            defaults={"role": User.Role.ADMIN, "display_name": "Admin", "is_staff": True, "is_superuser": True},
        )
        admin.set_password("12")
        admin.save()

        company_user, _ = User.objects.update_or_create(
            username="company1",
            defaults={
                "role": User.Role.COMPANY,
                "company": companies["Oltin Saroy"],
                "display_name": "Oltin Saroy",
            },
        )
        company_user.set_password("12")
        company_user.save()

        product_rows = [
            ("p1", "💍", "Oltin Saroy", tr("Oltin uzuk", "Золотое кольцо", "Gold ring"), tr("24K oltin, qo'lda ishlangan", "Золото 24K, ручная работа", "24K gold, handcrafted"), "$1 200"),
            ("p2", "🪑", "Mebel Pro", tr("Yumshoq divan", "Мягкий диван", "Soft sofa"), tr("Premium teri qoplama", "Премиум кожаная обивка", "Premium leather"), "$850"),
            ("p3", "⌚", "Vaqt Lux", tr("Klassik soat", "Классические часы", "Classic watch"), tr("Shveytsariya mexanizmi", "Швейцарский механизм", "Swiss movement"), "$2 400"),
            ("p4", "👜", "Charm House", tr("Teri sumka", "Кожаная сумка", "Leather bag"), tr("Tabiiy teri, milliy uslub", "Натуральная кожа", "Genuine leather"), "$320"),
            ("p5", "🏺", "Hunarmand", tr("Sopol idish", "Керамическая ваза", "Ceramic vase"), tr("Qo'lda bo'yalgan", "Ручная роспись", "Hand-painted"), "$140"),
            ("p6", "🧶", "Atlas Silk", tr("Atlas mato", "Ткань Атлас", "Atlas silk"), tr("An'anaviy ipak", "Традиционный шёлк", "Traditional silk"), "$95"),
            ("p7", "💻", "TechNation", tr("Noutbuk Pro", "Ноутбук Pro", "Laptop Pro"), tr("Mahalliy yig'ilgan", "Местная сборка", "Locally assembled"), "$1 050"),
            ("p8", "🍯", "Asal Bio", tr("Tog' asali", "Горный мёд", "Mountain honey"), tr("100% tabiiy", "100% натуральный", "100% natural"), "$25"),
        ]
        for legacy_id, icon, company, name, desc, price in product_rows:
            Product.objects.update_or_create(
                legacy_id=legacy_id,
                defaults={
                    "company": companies[company],
                    "icon": icon,
                    "name_i18n": name,
                    "description_i18n": desc,
                    "price_label": price,
                },
            )

        news_rows = [
            ("n1", "📈", "Oltin Saroy", date(2026, 7, 1), tr("Bugungi oltin kursi", "Курс золота на сегодня", "Gold rate today"), tr("1 gr oltin narxi 2% ga oshdi.", "Цена 1 г золота выросла на 2%.", "Price of 1g gold rose 2%.")),
            ("n2", "🤝", "Konglomerat", date(2026, 6, 30), tr("Yangi eksport shartnomasi", "Новый экспортный контракт", "New export deal"), tr("3 kompaniya Markaziy Osiyo bozoriga chiqdi.", "3 компании вышли на рынок ЦА.", "3 firms entered the Central Asian market.")),
            ("n3", "🚀", "TechNation", date(2026, 6, 28), tr("Startap aksellerator ochildi", "Открыт стартап-акселератор", "Startup accelerator opens"), tr("12 yangi loyiha qabul qilindi.", "Принято 12 новых проектов.", "12 new projects accepted.")),
            ("n4", "🏭", "Mebel Pro", date(2026, 6, 25), tr("Yangi fabrika ishga tushdi", "Запущена новая фабрика", "New factory launched"), tr("500 ish o'rni yaratildi.", "Создано 500 рабочих мест.", "500 jobs created.")),
        ]
        for legacy_id, icon, company, published_on, title, summary in news_rows:
            NewsArticle.objects.update_or_create(
                legacy_id=legacy_id,
                defaults={
                    "company": companies.get(company),
                    "publisher_name": company,
                    "icon": icon,
                    "title_i18n": title,
                    "summary_i18n": summary,
                    "body_i18n": {k: [v] for k, v in summary.items()},
                    "published_on": published_on,
                },
            )

        for legacy_id, name, conf_date, conf_time, joined in [
            ("c1", "Q3 Strategy Sync", date(2026, 7, 3), time(15, 0), 30),
            ("c2", "Export Council", date(2026, 7, 5), time(11, 30), 12),
        ]:
            Conference.objects.update_or_create(
                legacy_id=legacy_id,
                defaults={"name": name, "date": conf_date, "time": conf_time, "capacity_total": 30},
            )

        complaint_rows = [
            ("cm1", "Charm House", "info@charmhouse.uz", "Delivery delayed", "Order #4521 was placed 5 days ago but still has not been delivered."),
            ("cm2", "Vaqt Lux", "+998 90 000 00 02", "Site is slow", "The company site loads very slowly, especially the product catalog."),
            ("cm3", "Hunarmand", "hunarmand@mail.uz", "Payment error", "Card payments fail even though there are sufficient funds."),
            ("cm4", "Atlas Silk", "+998 90 000 00 04", "Missing product photo", "Several showroom products have no photos."),
            ("cm5", "Asal Bio", "asal@bio.uz", "Report failed to load", "The monthly report will not open."),
        ]
        for legacy_id, from_name, contact, title, text in complaint_rows:
            Complaint.objects.update_or_create(
                legacy_id=legacy_id,
                defaults={
                    "from_company": companies.get(from_name),
                    "from_name": from_name,
                    "contact": contact,
                    "subject_i18n": tr(title, title, title),
                    "raw_message": text,
                    "status": Complaint.Status.PENDING,
                },
            )

        rnd_rows = [
            ("r1", "TechNation", "AI / IoT", tr("Aqlli logistika", "Умная логистика", "Smart logistics"), tr("Yetkazib berishni optimallashtirish.", "Оптимизация доставки.", "Delivery optimization.")),
            ("r2", "Asal Bio", "GreenTech", tr("Eko qadoqlash", "Эко-упаковка", "Eco packaging"), tr("Bioparchalanuvchi materiallar.", "Биоразлагаемые материалы.", "Biodegradable materials.")),
        ]
        for legacy_id, company, category, name, desc in rnd_rows:
            RndSubmission.objects.update_or_create(
                legacy_id=legacy_id,
                defaults={
                    "company": companies[company],
                    "category": category,
                    "name_i18n": name,
                    "description_i18n": desc,
                },
            )

        counts = [8, 8, 9, 7, 8, 7, 8, 7, 8, 8, 8, 7, 7]
        for block_index, count in enumerate(counts):
            for module_index in range(count):
                ManagementModule.objects.update_or_create(
                    key=f"m-{block_index}-{module_index}",
                    defaults={
                        "block_index": block_index,
                        "module_index": module_index,
                        "enabled": module_index % 3 != 0,
                    },
                )

        group, _ = ChatThread.objects.get_or_create(
            kind=ChatThread.Kind.GROUP,
            company=None,
            defaults={"title": "Group chat"},
        )
        direct, _ = ChatThread.objects.get_or_create(
            kind=ChatThread.Kind.ADMIN_COMPANY,
            company=companies["Oltin Saroy"],
            defaults={"title": "Admin · Oltin Saroy"},
        )
        for legacy_id, thread, sender, text_value in [
            ("g1", group, company_user, "Курс золота обновлён ✅"),
            ("g2", group, company_user, "Готовим демо стартапов к пятнице."),
            ("g3", group, admin, "Всем добрый день! Конференция в 15:00."),
            ("i1", direct, company_user, "Здравствуйте, отчёт готов."),
            ("i2", direct, admin, "Отлично, проверю сегодня."),
        ]:
            ChatMessage.objects.get_or_create(
                legacy_id=legacy_id,
                defaults={"thread": thread, "sender": sender, "text": text_value},
            )

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
