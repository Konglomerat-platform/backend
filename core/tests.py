from django.test import TestCase
from django.urls import reverse


class SchemaGenerationTests(TestCase):
    def test_openapi_schema_generates_without_warnings(self):
        response = self.client.get(reverse("schema"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "openapi: 3.0.3")
