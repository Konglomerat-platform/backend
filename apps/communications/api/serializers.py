from rest_framework import serializers

from apps.communications.models import ChatMessage, ChatThread
from core.utils import external_id, localized_file_url


class ChatMessageSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    databaseId = serializers.IntegerField(source="id", read_only=True)
    chat = serializers.SerializerMethodField()
    sender = serializers.CharField(source="sender.public_name")
    role = serializers.CharField(source="sender.role")
    data = serializers.SerializerMethodField()
    dur = serializers.SerializerMethodField()
    seenBy = serializers.SerializerMethodField()
    ts = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = (
            "id",
            "databaseId",
            "chat",
            "sender",
            "role",
            "kind",
            "text",
            "data",
            "name",
            "dur",
            "seenBy",
            "edited",
            "ts",
        )

    def get_id(self, obj: ChatMessage) -> str:
        return external_id(obj)

    def get_chat(self, obj: ChatMessage) -> str:
        if obj.thread.kind == ChatThread.Kind.GROUP:
            return "group"
        return obj.thread.company.name

    def get_data(self, obj: ChatMessage) -> str | None:
        return localized_file_url(self.context.get("request"), obj.file)

    def get_dur(self, obj: ChatMessage) -> float | None:
        return float(obj.duration_seconds or 0) if obj.duration_seconds else None

    def get_seenBy(self, obj: ChatMessage) -> list[dict[str, str]]:
        return [{"name": receipt.user.public_name, "at": receipt.seen_at.isoformat()} for receipt in obj.receipts.all()]

    def get_ts(self, obj: ChatMessage) -> int:
        return int(obj.created_at.timestamp() * 1000)
