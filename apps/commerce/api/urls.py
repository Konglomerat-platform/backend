from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.commerce.api.views import FavoritesViewSet, OrderViewSet

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [
    *router.urls,
    path("favorites/", FavoritesViewSet.as_view({"get": "list", "put": "replace"}), name="favorites"),
]
