# Front/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import User, Reward

class UserCoinsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_group_name = f'user_{self.user_id}'

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({
            'message': 'This is a one-way communication WebSocket'
        }))

    async def user_coins_update(self, event):
        await self.send(text_data=json.dumps(event['data']))
