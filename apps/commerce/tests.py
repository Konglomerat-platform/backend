from django.test import TestCase
from rest_framework.test import APIClient

from apps.catalog.models import Product
from apps.companies.models import Company
from apps.commerce.models import Order
from apps.notifications.models import Notification


class OrderApiTests(TestCase):
    def test_create_order_creates_company_and_admin_notifications(self):
        company = Company.objects.create(name="Acme", slug="acme")
        product = Product.objects.create(
            legacy_id="p1",
            company=company,
            name_i18n={"en": "Box"},
            price_label="$10",
        )

        response = APIClient().post(
            "/api/orders/",
            {"productId": product.legacy_id, "name": "Buyer", "contact": "buyer@example.com", "qty": 2},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(response.data["qty"], 2)
