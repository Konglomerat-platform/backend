from rest_framework import serializers

from apps.content.models import NewsArticle
from core.utils import external_id, localized_file_url


class NewsArticleSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    databaseId = serializers.IntegerField(source="id", read_only=True)
    ico = serializers.CharField(source="icon")
    company = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    title = serializers.JSONField(source="title_i18n")
    text = serializers.SerializerMethodField()
    body = serializers.JSONField(source="body_i18n")
    images = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = ("id", "databaseId", "ico", "company", "date", "title", "text", "body", "images", "image")

    def get_id(self, obj: NewsArticle) -> str:
        return external_id(obj)

    def get_company(self, obj: NewsArticle) -> str:
        return obj.company.name if obj.company_id else obj.publisher_name

    def get_date(self, obj: NewsArticle) -> str:
        return obj.published_on.isoformat()

    def get_text(self, obj: NewsArticle) -> dict:
        return {
            lang: value[0] if isinstance(value, list) and value else value
            for lang, value in obj.summary_i18n.items()
        } or obj.summary_i18n

    def get_images(self, obj: NewsArticle) -> list[str]:
        request = self.context.get("request")
        urls = [localized_file_url(request, image.file) for image in obj.images.all()]
        return [url for url in urls if url]

    def get_image(self, obj: NewsArticle) -> str | None:
        images = self.get_images(obj)
        return images[0] if images else None
