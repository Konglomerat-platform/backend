from rest_framework import serializers

from apps.companies.models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("id", "name", "slug", "sector", "email", "phone", "active", "metadata")
        read_only_fields = ("id",)
