from __future__ import annotations

from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from apps.communications.events import chat_group_name
from apps.communications.services import thread_for_chat


@database_sync_to_async
def _thread_for_chat(chat: str, user):
    return thread_for_chat(chat, user)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        params = parse_qs(self.scope.get("query_string", b"").decode())
        self.chat = (params.get("chat") or [""])[0]
        thread = await _thread_for_chat(self.chat, user)
        if not thread:
            await self.close(code=4403)
            return

        self.thread_id = thread.id
        self.group_name = chat_group_name(thread.id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        group_name = getattr(self, "group_name", None)
        if group_name:
            await self.channel_layer.group_discard(group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get("type") == "ping":
            await self.send_json({"type": "pong"})

    async def chat_event(self, event):
        await self.send_json(event["payload"])
