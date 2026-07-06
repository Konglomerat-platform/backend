from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def chat_group_name(thread_id: int) -> str:
    return f"chat_thread_{thread_id}"


def broadcast_chat_event(thread_id: int, event_type: str, payload: dict) -> None:
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        chat_group_name(thread_id),
        {
            "type": "chat.event",
            "payload": {"type": event_type, **payload},
        },
    )
