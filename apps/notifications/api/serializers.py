from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.JSONField(source="title_i18n")
    at = serializers.SerializerMethodField()
    read = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ("id", "title", "text", "link", "at", "read")

    def get_at(self, obj: Notification) -> str:
        return obj.created_at.isoformat()

    def get_read(self, obj: Notification) -> bool:
        return obj.id in self.context.get("read_ids", set())
