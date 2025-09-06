# app/consumers.py
import json
import re
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Message

def clean_room_name(name):
    """Sanitize room name for Channels group (only ASCII letters, numbers, hyphen, underscore, period)"""
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', name)[:100]

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name_raw = self.scope['url_route']['kwargs']['room_name']
        self.room_name = clean_room_name(self.room_name_raw)
        self.group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        # Optionally: send last 50 messages on connect
        last_messages = await self.get_last_messages()
        for msg in last_messages:
            await self.send(text_data=json.dumps({
                "user": msg.user.username if msg.user else "Anonymous",
                "message": msg.content
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '').strip()
        user = self.scope["user"] if self.scope["user"].is_authenticated else None
        if message:
            # Save message in DB
            msg = await self.save_message(user, message)

            # Broadcast to group
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': msg.content,
                    'user': msg.user.username if msg.user else "Anonymous"
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user': event['user']
        }))

    @database_sync_to_async
    def save_message(self, user, content):
        return Message.objects.create(room_name=self.room_name_raw, user=user, content=content)

    @database_sync_to_async
    def get_last_messages(self):
        return Message.objects.filter(room_name=self.room_name_raw).order_by('-timestamp')[:50][::-1]
