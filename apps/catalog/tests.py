from django.test import TestCase
from rest_framework.test import APIClient

from apps.catalog.models import Product, ProductImage
from apps.companies.models import Company
from apps.users.models import User


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

    def test_company_product_create_keeps_up_to_eight_images(self):
        company = Company.objects.create(name="Acme", slug="acme")
        user = User.objects.create_user(username="company", role=User.Role.COMPANY, company=company)
        client = APIClient()
        client.force_authenticate(user=user)
        images = ["data:image/png;base64,cG5n" for _ in range(9)]

        response = client.post(
            "/api/products/",
            {"name": {"en": "Album"}, "desc": {"en": "Many photos"}, "price": "$12", "images": images},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data["images"]), 8)
        self.assertEqual(ProductImage.objects.count(), 8)
