from django.urls import include, path

from core.api import health

urlpatterns = [
    path("health/", health, name="health"),
    path("", include("apps.users.api.urls")),
    path("", include("apps.companies.api.urls")),
    path("", include("apps.catalog.api.urls")),
    path("", include("apps.content.api.urls")),
    path("", include("apps.commerce.api.urls")),
    path("", include("apps.support.api.urls")),
    path("", include("apps.innovation.api.urls")),
    path("", include("apps.communications.api.urls")),
    path("", include("apps.operations.api.urls")),
    path("", include("apps.notifications.api.urls")),
    path("", include("apps.ai.api.urls")),
]
