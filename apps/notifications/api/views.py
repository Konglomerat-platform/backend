from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.notifications.api.serializers import NotificationSerializer
from apps.notifications.models import Notification
from apps.notifications.models import NotificationRead
from apps.notifications.services import mark_all_read, visible_notifications


class NotificationViewSet(ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        return visible_notifications(self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if getattr(self, "swagger_fake_view", False):
            context["read_ids"] = set()
            return context
        context["read_ids"] = set(
            NotificationRead.objects.filter(user=self.request.user).values_list("notification_id", flat=True)
        )
        return context

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        items = serializer.data
        return Response({"list": items, "unread": len([item for item in items if not item["read"]])})

    @action(detail=False, methods=["post"], url_path="read")
    def read(self, request):
        mark_all_read(request.user)
        return Response({"ok": True})
