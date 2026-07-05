from django.test import TestCase
from rest_framework.test import APIClient

from apps.catalog.models import Product
from apps.companies.models import Company


class ProductApiTests(TestCase):
    def test_product_list_returns_legacy_payload_shape(self):
        company = Company.objects.create(name="Acme", slug="acme")
        Product.objects.create(
            legacy_id="p1",
            company=company,
            icon="box",
            name_i18n={"en": "Box", "ru": "Box", "uz": "Box"},
            description_i18n={"en": "Useful", "ru": "Useful", "uz": "Useful"},
            price_label="$10",
        )

        response = APIClient().get("/api/products/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], "p1")
        self.assertEqual(response.data[0]["company"], "Acme")
        self.assertEqual(response.data[0]["name"]["en"], "Box")
