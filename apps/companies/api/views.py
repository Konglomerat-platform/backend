from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.companies.api.serializers import CompanySerializer
from apps.companies.models import Company


class CompanyViewSet(ReadOnlyModelViewSet):
    queryset = Company.objects.filter(active=True)
    serializer_class = CompanySerializer
    filterset_fields = ("sector", "active")
