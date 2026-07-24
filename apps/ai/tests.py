from django.test import TestCase
from rest_framework.test import APIClient

from apps.catalog.models import Product
from apps.companies.models import Company
from apps.users.models import User


class AiCompanyCountTests(TestCase):
    """The assistant must count companies, not recite a memorised figure."""

    def setUp(self):
        self.with_products = Company.objects.create(name="Alpha", slug="alpha")
        self.without_products = Company.objects.create(name="Beta", slug="beta")
        Company.objects.create(name="Dormant", slug="dormant", active=False)
        Product.objects.create(legacy_id="p1", company=self.with_products, price_label="$1")
        self.user = User.objects.create_user(username="u1", role=User.Role.COMPANY)

    def _ask(self, message):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post("/api/ai/chat/", {"message": message, "lang": "en"}, format="json")
        self.assertEqual(response.status_code, 200)
        return response.data["reply"]

    def test_platform_description_uses_the_live_active_company_count(self):
        reply = self._ask("what is konglomerat")

        self.assertIn("2 companies", reply)
        self.assertNotIn("30 companies", reply)

    def test_company_listing_counts_companies_without_products(self):
        # "company" (singular) is what the intent regex matches.
        reply = self._ask("show me the company list")

        # Beta has no products; the old implementation derived the list from
        # distinct product owners and would have reported only 1.
        self.assertIn("2 companies", reply)
        self.assertIn("Alpha", reply)
        self.assertIn("Beta", reply)

    def test_company_count_is_exact_and_not_suffixed_with_a_plus(self):
        reply = self._ask("show me the company list")

        self.assertNotIn("+", reply)

    def test_counts_fall_to_zero_on_an_empty_platform(self):
        # Product holds a PROTECT reference to Company, so clear it first.
        Product.objects.all().delete()
        Company.objects.all().delete()

        reply = self._ask("what is konglomerat")

        self.assertIn("0 companies", reply)
