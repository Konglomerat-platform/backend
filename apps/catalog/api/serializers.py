from rest_framework import serializers

from apps.catalog.models import Product
from core.utils import external_id, localized_file_url


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    databaseId = serializers.IntegerField(source="id", read_only=True)
    ico = serializers.CharField(source="icon")
    company = serializers.CharField(source="company.name")
    companyId = serializers.IntegerField(source="company_id")
    name = serializers.JSONField(source="name_i18n")
    desc = serializers.JSONField(source="description_i18n")
    description = serializers.JSONField(source="description_i18n")
    price = serializers.CharField(source="price_label")
    priceAmount = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "databaseId",
            "ico",
            "icon",
            "company",
            "companyId",
            "name",
            "desc",
            "description",
            "price",
            "priceAmount",
            "currency",
            "images",
            "image",
            "createdAt",
        )

    def get_id(self, obj: Product) -> str:
        return external_id(obj)

    def get_priceAmount(self, obj: Product) -> str | None:
        return str(obj.price_amount) if obj.price_amount is not None else None

    def get_images(self, obj: Product) -> list[str]:
        request = self.context.get("request")
        urls = [localized_file_url(request, image.file) for image in obj.images.all()]
        return [url for url in urls if url]

    def get_image(self, obj: Product) -> str | None:
        images = self.get_images(obj)
        return images[0] if images else None

    def get_createdAt(self, obj: Product) -> str:
        return obj.created_at.isoformat()
