from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.content.api.serializers import NewsArticleSerializer
from apps.content.models import NewsArticle
from apps.content.services import create_news, delete_news, update_news
from core.utils import get_by_external


class NewsArticleViewSet(ModelViewSet):
    serializer_class = NewsArticleSerializer
    permission_classes = [AllowAny]
    lookup_value_regex = r"[^/]+"

    def get_queryset(self):
        return NewsArticle.objects.select_related("company").prefetch_related("images")

    def get_object(self):
        article = get_by_external(NewsArticle, self.kwargs[self.lookup_field])
        if not article:
            raise NotFound()
        self.check_object_permissions(self.request, article)
        return article

    def create(self, request, *args, **kwargs):
        article = create_news(request.user, request.data)
        return Response(self.get_serializer(article).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        article = update_news(request.user, kwargs[self.lookup_field], request.data)
        return Response(self.get_serializer(article).data)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        delete_news(request.user, kwargs[self.lookup_field])
        return Response({"ok": True})
