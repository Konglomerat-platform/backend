from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.operations.api.views import (
    ConferenceViewSet,
    ManagementModuleViewSet,
    ReportGenerateView,
    StatsView,
)

router = DefaultRouter()
router.register("conferences", ConferenceViewSet, basename="conference")
router.register("management-modules", ManagementModuleViewSet, basename="management-module")

urlpatterns = [
    path("stats/", StatsView.as_view(), name="stats"),
    path("reports/generate/", ReportGenerateView.as_view(), name="report-generate"),
    *router.urls,
]
