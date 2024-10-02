# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# import redis.asyncio as redis

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f'chat_{self.room_name}'

#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)

#         await self.accept()

#         self.redis = await redis.from_url('redis://localhost:6379', decode_responses=True)

#         messages = await self.redis.lrange(f'chat_{self.room_name}_messages', 0, -1)

#         for message in messages:
#             await self.send(text_data=message)

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#         username = self.scope['user'].username if self.scope['user'].is_authenticated else 'Anonyme'

#         formatted_message = json.dumps({
#             'message': message,
#             'username' : username
#         })

#         await self.redis.rpush(f'chat_{self.room_name}_messages', formatted_message)

#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'username' : username,
#             }
#         )

#     async def chat_message(self, event):
#         message = event['message']
#         username = event['username']

#         await self.send(text_data=json.dumps({
#             'message': message,
#             'username' : username
#         }))



import json
from channels.generic.websocket import AsyncWebsocketConsumer
import redis.asyncio as redis

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Ajouter le consommateur à la salle
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Connexion à Redis
        self.redis = redis.Redis(host="redis", decode_responses=True)

        # Récupérer l'historique des messages de Redis
        messages = await self.redis.lrange(f'chat_{self.room_name}_messages', 0, -1)

        # Envoyer l'historique au client
        for message in messages:
            # Les messages sont déjà encodés en JSON lorsqu'ils sont stockés dans Redis
            await self.send(text_data=message)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['user'].username if self.scope['user'].is_authenticated else 'Anonyme'

        # Formater le message
        formatted_message = json.dumps({
            'message': message,
            'username': username
        })

        # Stocker le message dans Redis
        await self.redis.rpush(f'chat_{self.room_name}_messages', formatted_message)

        # Envoyer le message à tous les clients connectés
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Envoyer le message formaté au client
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))
