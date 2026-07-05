from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.communications.api.serializers import ChatMessageSerializer
from apps.communications.models import ChatMessage
from apps.communications.services import (
    create_message,
    delete_message,
    mark_seen,
    messages_for_chat,
    update_message,
)


class ChatMessageViewSet(GenericViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    lookup_value_regex = r"[^/]+"

    def get_queryset(self):
        return ChatMessage.objects.select_related("sender", "thread__company").prefetch_related("receipts__user")

    def list(self, request):
        messages = messages_for_chat(request.query_params.get("chat") or "", request.user)
        return Response(self.get_serializer(messages, many=True).data)

    def create(self, request):
        message = create_message(request.user, request.data)
        return Response(self.get_serializer(message).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        message = update_message(request.user, kwargs[self.lookup_field], request.data)
        return Response(self.get_serializer(message).data)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        delete_message(request.user, kwargs[self.lookup_field])
        return Response({"ok": True})

    @action(detail=False, methods=["post"])
    def seen(self, request):
        mark_seen(request.user, request.data.get("chat") or "")
        return Response({"ok": True})
