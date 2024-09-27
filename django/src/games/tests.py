from django.test import TestCase
from channels.testing import WebsocketCommunicator
from core.asgi import application
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

class PongTest(TestCase):
	async def test_anonymous_connection(self):
		communicator = WebsocketCommunicator(application, "/ws/pong/")
		connected, subprotocol = await communicator.connect()
		self.assertFalse(connected)
		await communicator.disconnect()

	async def test_connection_missing_params(self):
		test_user = await sync_to_async(get_user_model().objects.create_user)(
        	username="testuser", password="testpassword"
    	)
		communicator = WebsocketCommunicator(application, "/ws/pong/")
		communicator.scope["user"] = test_user
		connected, subprotocol = await communicator.connect()
		self.assertFalse(connected)
		await communicator.disconnect()
