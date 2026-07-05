from django.test import TestCase
from rest_framework.test import APIClient

from apps.companies.models import Company
from apps.innovation.models import RndSubmission
from apps.users.models import User


class RndSubmissionApiTests(TestCase):
    def test_company_can_create_and_admin_can_review_submission(self):
        company = Company.objects.create(name="Acme", slug="acme")
        company_user = User.objects.create_user(username="company", role=User.Role.COMPANY, company=company)
        admin = User.objects.create_user(username="admin", role=User.Role.ADMIN)
        client = APIClient()
        client.force_authenticate(user=company_user)

        created = client.post(
            "/api/rnd-submissions/",
            {"cat": "AI", "name": "Idea", "desc": "Better flow", "patent": True},
            format="json",
        )
        self.assertEqual(created.status_code, 201)

        client.force_authenticate(user=admin)
        updated = client.put(
            f"/api/rnd-submissions/{created.data['id']}/",
            {"status": RndSubmission.Status.APPROVED},
            format="json",
        )

        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["status"], RndSubmission.Status.APPROVED)
