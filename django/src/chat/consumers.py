import json
from channels.generic.websocket import AsyncWebsocketConsumer
import redis.asyncio as redis

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['user'].username if self.scope['user'].is_authenticated else 'Anonyme'
        self.redis = redis.Redis(host="redis", decode_responses=True)

        if self.scope['url_route']['kwargs'].get('username'):
            other_username = self.scope['url_route']['kwargs']['username']
            users = sorted([self.username, other_username])
            self.room_group_name = f'private_chat_{users[0]}_{users[1]}'
        else:
            self.room_group_name = 'chat_general'

        await self.channel_layer.group_add(f'user_{self.username}', self.channel_name)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.add_active_user()
        await self.accept()
        await self.broadcast_active_users()

        if self.scope['url_route']['kwargs'].get('username'):
            await self.notify_other_user(other_username)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(f'user_{self.username}', self.channel_name)
        await self.remove_active_user()
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.broadcast_active_users()
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

    async def notify_other_user(self, other_username):
        other_user_channel = f'user_{other_username}'
        await self.channel_layer.group_send(
            other_user_channel,
            {
                'type': 'private_message_notification',
                'from_user': self.username,
            }
        )

    async def send_chat_history(self, event=None):
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

    async def private_message_notification(self, event):
        from_user = event['from_user']
        await self.send(text_data=json.dumps({
            'type': 'private_message_notification',
            'from_user': from_user,
        }))

    async def add_active_user(self):
        await self.redis.sadd('active_users', self.username)

    async def remove_active_user(self):
        await self.redis.srem('active_users', self.username)

    async def broadcast_active_users(self):
        active_users = await self.redis.smembers('active_users')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_active_users',
                'users': list(active_users),
            }
        )

    async def send_active_users(self, event):
        users = event['users']
        await self.send(text_data=json.dumps({
            'type': 'active_users',
            'users': users
        }))
