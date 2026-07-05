from rest_framework.routers import DefaultRouter

from apps.content.api.views import NewsArticleViewSet

router = DefaultRouter()
router.register("news", NewsArticleViewSet, basename="news")

urlpatterns = router.urls
