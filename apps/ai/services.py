from __future__ import annotations

import re
from datetime import date

KONG_TOPIC = re.compile(
    r"konglomerat|конгломерат|kompan|компан|company|firm|business|biznes|"
    r"mahsulot|товар|product|showroom|catalog|eksport|export|invest|startup|"
    r"loyiha|проект|report|hisobot|отч[её]т|conference|meeting|news|"
    r"complaint|shikoyat|жалоб|r&d|patent|analytics|director|platform|module|"
    r"price|narx|oltin|mebel|technation|asal|what is|about|nima",
    re.IGNORECASE,
)
GREETING = re.compile(
    r"^\s*(salom|assalom|привет|здравствуй|добрый|hello|hi|hey)", re.IGNORECASE
)


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


def on_topic(message: str) -> bool:
    return bool(KONG_TOPIC.search(message or "") or GREETING.search(message or ""))


def ai_reply(message: str, lang: str, *, products, news, conferences, complaints, rnd, companies) -> str:
    lang = lang if lang in {"uz", "ru", "en"} else "ru"
    q = (message or "").lower()

    def t(uz: str, ru: str, en: str) -> str:
        return {"uz": uz, "ru": ru, "en": en}[lang]

    if GREETING.search(q):
        return t(
            "Salom! Men Konglomerat biznes AI yordamchisiman.",
            "Здравствуйте! Я бизнес-AI Konglomerat.",
            "Hello! I am the Konglomerat business AI.",
        )

    if re.search(r"what is|nima|about|konglomerat|конгломерат", q):
        # Counted live: this sentence used to assert a hardcoded 30, which
        # contradicted the real figure the same site publishes at /api/stats/.
        total = companies.count()
        return t(
            f"Konglomerat - {total} kompaniyani yagona boshqaruv ostida birlashtiruvchi platforma.",
            f"Konglomerat - платформа, объединяющая {total} компаний под единым управлением.",
            f"Konglomerat is a platform uniting {total} companies under one management system.",
        )

    if re.search(r"company|kompan|компан|firm", q):
        # Names come from the company table, not from distinct product owners:
        # the latter silently hid every company that has no products yet. The
        # trailing "+" is gone because the count is now exact.
        names = list(companies.values_list("name", flat=True))
        total = len(names)
        return t(
            f"Platformada {total} ta kompaniya bor: {', '.join(names[:8])}.",
            f"На платформе {total} компаний: {', '.join(names[:8])}.",
            f"The platform has {total} companies: {', '.join(names[:8])}.",
        )

    if re.search(r"product|mahsulot|товар|catalog|price|narx", q):
        sample = [f"{loc(p.name_i18n, lang)} - {p.price_label}" for p in products[:5]]
        return t(
            f"Katalogda {products.count()} ta mahsulot bor. Masalan: {'; '.join(sample)}.",
            f"В каталоге {products.count()} товаров. Например: {'; '.join(sample)}.",
            f"The catalog has {products.count()} products. For example: {'; '.join(sample)}.",
        )

    if re.search(r"news|yangilik|новост", q):
        item = news.first()
        if item:
            return t(
                f"So'nggi yangilik: {loc(item.title_i18n, lang)}.",
                f"Последняя новость: {loc(item.title_i18n, lang)}.",
                f"Latest news: {loc(item.title_i18n, lang)}.",
            )

    if re.search(r"conference|meeting|konferens|конференц", q):
        item = conferences.first()
        if item:
            return t(
                f"Yaqin konferensiya: {item.name} - {item.date} {item.time}.",
                f"Ближайшая конференция: {item.name} - {item.date} {item.time}.",
                f"Upcoming conference: {item.name} - {item.date} {item.time}.",
            )

    if re.search(r"complaint|shikoyat|жалоб|problem|muammo", q):
        pending = complaints.filter(status="pending").count()
        return t(
            f"Hozir {pending} ta ochiq shikoyat bor.",
            f"Сейчас {pending} открытых жалоб.",
            f"There are {pending} open complaints.",
        )

    if re.search(r"r&d|rnd|startup|patent|loyiha|проект", q):
        return t(
            f"R&D markazida {rnd.count()} ta loyiha bor.",
            f"В R&D-центре {rnd.count()} проектов.",
            f"The R&D center has {rnd.count()} projects.",
        )

    return t(
        "Konglomerat ma'lumotlari asosida tahlil qilyapman.",
        "Анализирую на основе данных Konglomerat.",
        "Analyzing based on Konglomerat data.",
    )


def ai_letter(message: str, lang: str, company_name: str, attachments: list[dict] | None = None) -> dict:
    lang = lang if lang in {"uz", "ru", "en"} else "ru"
    q = (message or "").lower()

    def t(uz: str, ru: str, en: str) -> str:
        return {"uz": uz, "ru": ru, "en": en}[lang]

    if re.search(r"deliver|yetkaz|достав|delay|kechik|задерж", q):
        subject = t("Yetkazib berish muammosi", "Проблема доставки", "Delivery issue")
        analysis = t(
            "Yetkazib berishdagi uzilish mijoz ishonchiga ta'sir qiladi.",
            "Сбой доставки влияет на доверие клиента.",
            "Delivery disruption affects customer trust.",
        )
    elif re.search(r"payment|to'lov|плат|card|karta", q):
        subject = t("To'lov tizimi muammosi", "Проблема платежной системы", "Payment issue")
        analysis = t(
            "To'lovdagi xato daromad yo'qotilishiga olib kelishi mumkin.",
            "Платежная ошибка может привести к потере выручки.",
            "Payment failure can directly cause revenue loss.",
        )
    elif re.search(r"site|sayt|сайт|slow|sekin|медлен", q):
        subject = t("Sayt ishlashi muammosi", "Проблема работы сайта", "Website performance issue")
        analysis = t(
            "Sekin yuklanish konversiyani pasaytiradi.",
            "Медленная загрузка снижает конверсию.",
            "Slow loading reduces conversion.",
        )
    else:
        subject = t("Umumiy murojaat", "Общее обращение", "General matter")
        analysis = t(
            "Vaziyat kompaniya faoliyatiga ta'sir qilmoqda.",
            "Ситуация влияет на работу компании.",
            "The situation affects company operations.",
        )

    labels = {
        "header": t("RASMIY XAT", "ОФИЦИАЛЬНОЕ ПИСЬМО", "OFFICIAL LETTER"),
        "to": t("Kimga: Konglomerat ma'muriyati", "Кому: Администрация Konglomerat", "To: Konglomerat Administration"),
        "from": t("Kimdan", "От", "From"),
        "date": t("Sana", "Дата", "Date"),
        "subject": t("Mavzu", "Тема", "Subject"),
        "analysis": t("Tahlil", "Анализ", "Analysis"),
        "recommendations": t("Tavsiyalar", "Рекомендации", "Recommendations"),
        "regards": t("Hurmat bilan", "С уважением", "Sincerely"),
    }
    recommendation = t(
        "Mas'ul bo'limni jalb qilib, muddatli yechim rejasini tasdiqlashni so'raymiz.",
        "Просим привлечь ответственный отдел и утвердить план решения со сроками.",
        "Please involve the responsible team and approve a time-bound resolution plan.",
    )
    att_count = len(attachments or [])
    attachment_line = (
        "\n" + t(f"Ilovalar: {att_count}", f"Приложения: {att_count}", f"Attachments: {att_count}")
        if att_count
        else ""
    )
    letter = "\n".join(
        [
            labels["header"],
            "",
            labels["to"],
            f"{labels['from']}: {company_name}",
            f"{labels['date']}: {date.today().isoformat()}",
            f"{labels['subject']}: {subject}",
            "",
            message or "-",
            "",
            f"{labels['analysis']}: {analysis}",
            f"{labels['recommendations']}: {recommendation}",
            attachment_line,
            "",
            labels["regards"],
            company_name,
        ]
    ).strip()
    return {"subject": subject, "letter": letter}
