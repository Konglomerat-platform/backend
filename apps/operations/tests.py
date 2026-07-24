from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.ai.models import AiInteraction
from apps.catalog.models import Product
from apps.commerce.models import Order
from apps.companies.models import Company
from apps.innovation.models import RndSubmission
from apps.notifications.models import Notification
from apps.operations.models import Conference
from apps.support.models import Complaint
from apps.users.models import User


class ConferenceApiTests(TestCase):
    def test_create_conference_normalizes_bare_link_and_notifies_companies(self):
        admin = User.objects.create_user(username="admin", role=User.Role.ADMIN)
        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.post(
            "/api/conferences/",
            {"name": "Meet", "date": "2026-07-08", "time": "10:00", "link": "meet.google.com/abc"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["link"], "https://meet.google.com/abc")
        self.assertEqual(Conference.objects.get().link, "https://meet.google.com/abc")
        self.assertEqual(Notification.objects.get().link, "https://meet.google.com/abc")


class ReportMetricsTests(TestCase):
    """Reports must aggregate real orders, not emit a fixed sample payload."""

    def setUp(self):
        self.company = Company.objects.create(name="Alpha", slug="alpha")
        self.other = Company.objects.create(name="Beta", slug="beta")
        self.product = Product.objects.create(
            legacy_id="p1", company=self.company, price_label="$10", price_amount="10.00"
        )
        self.other_product = Product.objects.create(
            legacy_id="p2", company=self.other, price_label="$99", price_amount="99.00"
        )
        self.user = User.objects.create_user(
            username="c1", role=User.Role.COMPANY, company=self.company
        )

    def _order(self, product, company, quantity, *, days_ago=0):
        order = Order.objects.create(
            product=product, company=company, quantity=quantity, customer_name="X", customer_contact="y"
        )
        if days_ago:
            Order.objects.filter(pk=order.pk).update(
                created_at=timezone.now() - timedelta(days=days_ago)
            )
        return order

    def test_company_report_sums_only_that_companys_orders(self):
        self._order(self.product, self.company, 3)  # 3 x 10.00 = 30.00
        self._order(self.other_product, self.other, 5)  # belongs to another company

        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post("/api/reports/generate/")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["revenue"], "30.00")
        self.assertEqual(response.data["orders"], 1)
        self.assertEqual(response.data["currency"], "USD")
        self.assertEqual(response.data["scope"], "Alpha")

    def test_growth_is_null_without_a_prior_period_baseline(self):
        self._order(self.product, self.company, 1)

        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post("/api/reports/generate/")

        self.assertIsNone(response.data["growth"])

    def test_growth_compares_against_the_preceding_period(self):
        self._order(self.product, self.company, 2, days_ago=45)  # prior window: 20.00
        self._order(self.product, self.company, 3)  # current window: 30.00

        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post("/api/reports/generate/")

        self.assertEqual(response.data["revenue"], "30.00")
        self.assertEqual(response.data["growth"], "+50.0%")

    def test_empty_company_reports_zero_rather_than_sample_figures(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post("/api/reports/generate/")

        self.assertEqual(response.data["revenue"], "0.00")
        self.assertEqual(response.data["orders"], 0)
        self.assertIsNone(response.data["growth"])
        self.assertNotIn("$48K", str(response.data.values()))

    def test_products_without_a_numeric_price_do_not_break_the_aggregate(self):
        unpriced = Product.objects.create(
            legacy_id="p3", company=self.company, price_label="on request", price_amount=None
        )
        self._order(self.product, self.company, 1)  # 10.00
        self._order(unpriced, self.company, 4)  # contributes 0.00

        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post("/api/reports/generate/")

        self.assertEqual(response.data["revenue"], "10.00")
        self.assertEqual(response.data["orders"], 2)

    def test_admin_report_covers_every_company(self):
        self._order(self.product, self.company, 3)  # 30.00
        self._order(self.other_product, self.other, 1)  # 99.00

        admin = User.objects.create_user(username="root", role=User.Role.ADMIN)
        client = APIClient()
        client.force_authenticate(user=admin)
        response = client.post("/api/reports/generate/")

        self.assertEqual(response.data["scope"], "ALL")
        self.assertEqual(response.data["revenue"], "129.00")
        self.assertEqual(response.data["orders"], 2)


class StatsApiTests(TestCase):
    """The hero statistics must report what is in the database, nothing else."""

    def test_stats_report_true_counts(self):
        active = Company.objects.create(name="Alpha", slug="alpha", active=True)
        Company.objects.create(name="Beta", slug="beta", active=True)
        Company.objects.create(name="Dormant", slug="dormant", active=False)
        Product.objects.create(legacy_id="p1", company=active, price_label="$1")
        Product.objects.create(legacy_id="p2", company=active, price_label="$2")
        Product.objects.create(legacy_id="p3", company=active, price_label="$3")
        AiInteraction.objects.create(visitor_id="v1", prompt="hi")
        AiInteraction.objects.create(visitor_id="v2", prompt="hello")
        RndSubmission.objects.create(legacy_id="r1", company=active, category="AI")
        Complaint.objects.create(legacy_id="c1", from_name="X", status=Complaint.Status.PENDING)
        Conference.objects.create(legacy_id="k1", name="Sync", date="2026-07-08", time="10:00")

        response = APIClient().get("/api/stats/")

        self.assertEqual(response.status_code, 200)
        # Inactive companies are excluded; no floor of 30 is applied.
        self.assertEqual(response.data["companies"], 2)
        # Every AI request is one AiInteraction row; no floor of 4820.
        self.assertEqual(response.data["aiRequests"], 2)
        # No phantom "+ 10" added to R&D submissions.
        self.assertEqual(response.data["startups"], 1)
        self.assertEqual(response.data["showrooms"], 3)
        self.assertEqual(response.data["complaints"], 1)
        self.assertEqual(response.data["conferences"], 1)

    def test_stats_are_all_zero_on_an_empty_database(self):
        response = APIClient().get("/api/stats/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            dict(response.data),
            {
                "companies": 0,
                "aiRequests": 0,
                "startups": 0,
                "showrooms": 0,
                "complaints": 0,
                "conferences": 0,
            },
        )
