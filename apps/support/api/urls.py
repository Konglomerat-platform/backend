from rest_framework.routers import DefaultRouter

from apps.support.api.views import ComplaintViewSet

router = DefaultRouter()
router.register("complaints", ComplaintViewSet, basename="complaint")

urlpatterns = router.urls
