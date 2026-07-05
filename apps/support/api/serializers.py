from rest_framework import serializers

from apps.support.models import Complaint, ComplaintAttachment
from core.utils import external_id, localized_file_url


class ComplaintSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    databaseId = serializers.IntegerField(source="id", read_only=True)
    from_name = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()
    at = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = (
            "id",
            "databaseId",
            "from_name",
            "contact",
            "title",
            "text",
            "images",
            "attachments",
            "official",
            "reply",
            "status",
            "at",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["from"] = data.pop("from_name")
        data["reply"] = data["reply"] or None
        return data

    def get_id(self, obj: Complaint) -> str:
        return external_id(obj)

    def get_from_name(self, obj: Complaint) -> str:
        return obj.from_company.name if obj.from_company_id else obj.from_name

    def get_title(self, obj: Complaint):
        return obj.subject_i18n or None

    def get_text(self, obj: Complaint):
        return obj.message_i18n or obj.raw_message

    def get_images(self, obj: Complaint) -> list[str]:
        images = []
        for attachment in obj.attachments.all():
            if attachment.kind == ComplaintAttachment.Kind.IMAGE:
                url = localized_file_url(self.context.get("request"), attachment.file)
                if url:
                    images.append(url)
        return images

    def get_attachments(self, obj: Complaint) -> list[dict]:
        items = []
        for attachment in obj.attachments.all():
            items.append(
                {
                    "kind": attachment.kind,
                    "name": attachment.name,
                    "url": localized_file_url(self.context.get("request"), attachment.file),
                    "dur": float(attachment.duration_seconds or 0),
                }
            )
        return items

    def get_at(self, obj: Complaint) -> str:
        return obj.created_at.date().isoformat()
