from rest_framework import serializers

from apps.operations.models import Conference, ManagementModule, Report
from core.utils import external_id


class ConferenceSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    databaseId = serializers.IntegerField(source="id", read_only=True)
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    desc = serializers.CharField(source="description")
    joined = serializers.SerializerMethodField()
    total = serializers.IntegerField(source="capacity_total")

    class Meta:
        model = Conference
        fields = ("id", "databaseId", "name", "date", "time", "desc", "link", "joined", "total")

    def get_id(self, obj: Conference) -> str:
        return external_id(obj)

    def get_date(self, obj: Conference) -> str:
        return obj.date.isoformat()

    def get_time(self, obj: Conference) -> str:
        return obj.time.strftime("%H:%M")

    def get_joined(self, obj: Conference) -> int:
        return obj.attendances.count()


class ManagementModuleSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="key")

    class Meta:
        model = ManagementModule
        fields = ("id", "enabled")


class ReportSerializer(serializers.ModelSerializer):
    scope = serializers.SerializerMethodField()
    at = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ("id", "scope", "at")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(instance.metrics)
        return data

    def get_scope(self, obj: Report) -> str:
        return "ALL" if obj.scope == Report.Scope.ALL else obj.company.name

    def get_at(self, obj: Report) -> str:
        return obj.created_at.isoformat()
