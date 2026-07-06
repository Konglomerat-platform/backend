from pathlib import PurePath

from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.communications.api.serializers import ChatMessageSerializer
from apps.communications.events import broadcast_chat_event
from apps.communications.models import ChatMessage
from apps.communications.services import (
    create_message,
    delete_message,
    mark_seen,
    message_for_user,
    messages_for_chat,
    update_message,
)


class ChatMessageViewSet(GenericViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    lookup_value_regex = r"[^/]+"

    def get_queryset(self):
        return (
            ChatMessage.objects.select_related("sender", "thread__company", "parent__sender")
            .prefetch_related("receipts__user")
        )

    def list(self, request):
        messages = messages_for_chat(request.query_params.get("chat") or "", request.user)
        return Response(self.get_serializer(messages, many=True).data)

    def create(self, request):
        message = create_message(request.user, request.data)
        data = self.get_serializer(message).data
        broadcast_chat_event(message.thread_id, "message.created", {"message": data})
        return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        message = update_message(request.user, kwargs[self.lookup_field], request.data)
        data = self.get_serializer(message).data
        broadcast_chat_event(message.thread_id, "message.updated", {"message": data})
        return Response(data)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        message = delete_message(request.user, kwargs[self.lookup_field])
        broadcast_chat_event(message.thread_id, "message.deleted", {"id": str(kwargs[self.lookup_field])})
        return Response({"ok": True})

    @action(detail=False, methods=["post"])
    def seen(self, request):
        messages = mark_seen(request.user, request.data.get("chat") or "")
        if messages:
            data = self.get_serializer(messages, many=True).data
            broadcast_chat_event(messages[0].thread_id, "message.seen", {"messages": data})
        return Response({"ok": True})

    @action(detail=True, methods=["get"])
    def download(self, request, *args, **kwargs):
        message = message_for_user(request.user, kwargs[self.lookup_field])
        if not message.file:
            raise NotFound()
        filename = message.name or PurePath(message.file.name).name or "attachment"
        response = FileResponse(
            message.file.open("rb"),
            as_attachment=True,
            filename=filename,
            content_type=message.content_type or "application/octet-stream",
        )
        if message.size_bytes:
            response["Content-Length"] = str(message.size_bytes)
        return response
