from rest_framework import serializers

from apps.users.models import User


class UserPayloadSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "role", "name", "company")

    def get_name(self, obj: User) -> str:
        return obj.public_name

    def get_company(self, obj: User) -> dict | None:
        if not obj.company_id:
            return None
        return {"id": obj.company_id, "name": obj.company.name, "slug": obj.company.slug}
