import json
from channels.generic.websocket import AsyncWebsocketConsumer

class chatConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.room_type = self.scope['url_route']['kwargs']['room_type']
		self.room_name = self.scope['url_route']['kwargs']['room_name']

		if self.room_type == 'public':
			self.room_group_name = 'general_chat'
		elif self.room_type == 'private':
			self.room_group_name = f'private_{self.room_name}'
		elif self.room_type == 'tournament':
			self.room_group_name = f'tournament_{self.room_name}'
		
		await self.channel_layer.group_add(self.room_group_name, self.channel_name)

		await self.accept()

	async def disconnect(self, close_code):
			await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
	
	async def receive(self, msg_data):
		msg_data_json = json.loads(msg_data)
		msg = msg_data_json['message']

		await self.channel_layer.group_send(self.room_group_name, {'type': 'chat_msg', 'message': msg})

	async def chat_message(self, event):
		message = event['message']

		await self.send(text_data=json.dumps({'message' : message}))