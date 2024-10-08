import json
from channels.generic.websocket import AsyncWebsocketConsumer
import redis.asyncio as redis

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['user'].username if self.scope['user'].is_authenticated else 'Anonyme'
        self.redis = redis.Redis(host="redis", decode_responses=True)

        if self.scope['url_route']['kwargs'].get('chat_type', 'General') == 'General':
            self.room_group_name = 'chat_general'
        else:
            other_username = self.scope['url_route']['kwargs']['username']
            self.room_group_name = f'private_chat_{self.username}_{other_username}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.redis.close()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json.get('type') == 'fetch_history':
            await self.send_chat_history()
        else:
            message = text_data_json['message']
            username = self.scope['user'].username if self.scope['user'].is_authenticated else 'Anonyme'

            formatted_message = json.dumps({
                'message': message,
                'username': username
            })

            await self.redis.rpush(f'chat_{self.room_group_name}_messages', formatted_message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                }
            )
    
    async def send_chat_history(self):
        messages = await self.redis.lrange(f'chat_{self.room_group_name}_messages', 0, -1)
        history = [json.loads(message) for message in messages]

        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': history
        }))

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))
