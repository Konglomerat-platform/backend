from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.ai import llm
from apps.ai.services import build_context
from apps.catalog.models import Product
from apps.companies.models import Company
from apps.content.models import NewsArticle
from apps.innovation.models import RndSubmission
from apps.operations.models import Conference
from apps.support.models import Complaint
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


@override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-2.5-flash")
class AssistantLlmTests(TestCase):
    """The model is preferred; every failure degrades to the scripted reply."""

    def setUp(self):
        self.company = Company.objects.create(name="Alpha", slug="alpha")
        Product.objects.create(legacy_id="p1", company=self.company, price_label="$1")
        self.user = User.objects.create_user(username="u1", role=User.Role.COMPANY)
        llm.reset_client()
        self.addCleanup(llm.reset_client)

    def _ask(self, message="what is konglomerat"):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post(
            "/api/ai/chat/", {"message": message, "lang": "en"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        return response.data

    def test_model_answer_is_returned_and_not_marked_degraded(self):
        with patch("apps.ai.services.llm.generate", return_value="A live answer.") as gen:
            data = self._ask()

        self.assertEqual(data["reply"], "A live answer.")
        self.assertFalse(data["degraded"])
        gen.assert_called_once()

    def test_model_failure_falls_back_to_the_scripted_reply_and_flags_degraded(self):
        with patch("apps.ai.services.llm.generate", return_value=None):
            data = self._ask()

        self.assertIn("1 companies", data["reply"])
        self.assertTrue(data["degraded"])

    @override_settings(GEMINI_API_KEY="")
    def test_without_a_key_the_model_is_never_called(self):
        with patch("apps.ai.services.llm.generate") as gen:
            data = self._ask()

        gen.assert_not_called()
        self.assertTrue(data["degraded"])
        self.assertIn("1 companies", data["reply"])

    def test_offtopic_messages_do_not_reach_the_model(self):
        with patch("apps.ai.services.llm.generate") as gen:
            client = APIClient()
            client.force_authenticate(user=self.user)
            response = client.post(
                "/api/ai/chat/", {"message": "best pizza recipe", "lang": "en"}, format="json"
            )

        self.assertTrue(response.data["offtopic"])
        gen.assert_not_called()

    def test_an_sdk_exception_is_contained_rather_than_propagated(self):
        with patch("apps.ai.llm._get_client", side_effect=RuntimeError("boom")):
            with self.assertLogs("apps.ai.llm", level="ERROR"):
                data = self._ask()

        self.assertTrue(data["degraded"])
        self.assertIsNotNone(data["reply"])

    def test_blank_model_output_is_treated_as_failure(self):
        class _Empty:
            text = "   "

        with patch("apps.ai.llm._get_client") as client:
            client.return_value.models.generate_content.return_value = _Empty()
            with self.assertLogs("apps.ai.llm", level="WARNING"):
                data = self._ask()

        self.assertTrue(data["degraded"])


class ContextBlockTests(TestCase):
    """The DATA block must state counts separately from truncated samples."""

    def test_totals_are_explicit_and_samples_are_marked_as_partial(self):
        for i in range(12):
            Company.objects.create(name=f"C{i:02d}", slug=f"c{i:02d}")
        company = Company.objects.first()
        for i in range(7):
            Product.objects.create(legacy_id=f"p{i}", company=company, price_label="$1")

        context = build_context(
            products=Product.objects.select_related("company"),
            news=NewsArticle.objects.all(),
            conferences=Conference.objects.all(),
            complaints=Complaint.objects.all(),
            rnd=RndSubmission.objects.all(),
            companies=Company.objects.filter(active=True),
            lang="en",
        )

        self.assertIn("COMPANIES_TOTAL: 12", context)
        self.assertIn("PRODUCTS_TOTAL: 7", context)
        # Truncated lists must announce the truncation so the count cannot be
        # inferred from them.
        self.assertIn("showing 10 of 12", context)
        self.assertIn("showing 5 of 7", context)
        self.assertIn("NEWS_TOTAL: 0", context)
        self.assertIn("(none)", context)


class TimeoutClampTests(TestCase):
    """A misconfigured timeout must never mean 'unbounded'."""

    def test_zero_and_negative_are_clamped_to_a_positive_bound(self):
        for configured in (0, -5):
            with override_settings(GEMINI_TIMEOUT_SECONDS=configured):
                # google-genai treats a falsy timeout as no limit.
                self.assertGreaterEqual(llm._timeout_ms(), 1000)

    def test_configured_seconds_convert_to_integer_milliseconds(self):
        with override_settings(GEMINI_TIMEOUT_SECONDS=20):
            value = llm._timeout_ms()
        self.assertEqual(value, 20000)
        # The SDK field is typed int | None; a float fails validation.
        self.assertIsInstance(value, int)


class TopicGateTests(TestCase):
    """The gate decides whether a question reaches the model at all."""

    def test_plural_companies_is_on_topic(self):
        from apps.ai.services import on_topic

        for phrasing in (
            "how many companies",
            "how many companies are on the platform",
            "list the company names",
            "skolko kompaniy",
            "сколько компаний",
        ):
            self.assertTrue(on_topic(phrasing), phrasing)

    def test_unrelated_questions_stay_off_topic(self):
        from apps.ai.services import on_topic

        for phrasing in ("best pizza recipe", "who won the football match"):
            self.assertFalse(on_topic(phrasing), phrasing)


class ScriptedFallbackQualityTests(TestCase):
    """The fallback runs in production until a key is set, so it must answer."""

    def setUp(self):
        Company.objects.create(name="Alpha", slug="alpha")
        Company.objects.create(name="Beta", slug="beta")
        self.user = User.objects.create_user(username="u2", role=User.Role.COMPANY)

    def test_plural_phrasing_reaches_the_company_branch_not_the_generic_reply(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post(
            "/api/ai/chat/", {"message": "how many companies", "lang": "en"}, format="json"
        )

        self.assertTrue(response.data["degraded"])  # no key configured in tests
        self.assertIn("2 companies", response.data["reply"])
        self.assertNotIn("Analyzing based on", response.data["reply"])
