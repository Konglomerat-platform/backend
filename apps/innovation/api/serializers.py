from rest_framework import serializers

from apps.innovation.models import RndSubmission
from core.utils import external_id


class RndSubmissionSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    databaseId = serializers.IntegerField(source="id", read_only=True)
    company = serializers.CharField(source="company.name")
    cat = serializers.CharField(source="category")
    name = serializers.JSONField(source="name_i18n")
    desc = serializers.JSONField(source="description_i18n")
    patent = serializers.BooleanField(source="patent_requested")

    class Meta:
        model = RndSubmission
        fields = ("id", "databaseId", "company", "cat", "name", "desc", "patent", "status")

    def get_id(self, obj: RndSubmission) -> str:
        return external_id(obj)
