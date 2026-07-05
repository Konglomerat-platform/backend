from rest_framework.routers import DefaultRouter

from apps.innovation.api.views import RndSubmissionViewSet

router = DefaultRouter()
router.register("rnd-submissions", RndSubmissionViewSet, basename="rnd-submission")

urlpatterns = router.urls
