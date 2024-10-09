from channels.testing import ChannelsLiveServerTestCase, WebsocketCommunicator
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .pong import Game

class PongConsumerTest(ChannelsLiveServerTestCase):
    async def test_anonymous_user(self):
        """
        Test if anonymous user is rejected.
        """
        communicator = WebsocketCommunicator(Game.as_asgi(), "/ws/pong/?mode=local&player_needed=1")

        connected, _ = await communicator.connect()
        self.assertFalse(connected)

    async def test_wrong_user(self):
        """
        Test if wrong user is rejected.
        """
        communicator = WebsocketCommunicator(Game.as_asgi(), "/ws/pong/?mode=local&player_needed=1")
        communicator.scope['user'] = "wrong_user"

        connected, _ = await communicator.connect()
        self.assertFalse(connected)

    async def test_missing_parameters(self):
        """
        Test if wrong parameters request is rejected.
        """
        user = await sync_to_async(get_user_model().objects.create_user)(username='testuser', password='password123')
        communicator = WebsocketCommunicator(Game.as_asgi(), "/ws/pong/")
        communicator.scope['user'] = user

        connected, _ = await communicator.connect()
        self.assertFalse(connected)

    async def test_websocket_connect(self):
        """
        Test if the websocket consumer connects successfully.
        """
        user = await sync_to_async(get_user_model().objects.create_user)(username='testuser', password='password123')
        communicator = WebsocketCommunicator(Game.as_asgi(), "/ws/pong/?mode=local&player_needed=1&host=True&room_id=1")
        communicator.scope['user'] = user

        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "game_pad")

        await communicator.disconnect()

    async def test_invalid_message(self):
        """
        Test if the consumer handles invalid messages properly.
        """
        user = await sync_to_async(get_user_model().objects.create_user)(username='testuser', password='password123')
        communicator = WebsocketCommunicator(Game.as_asgi(), "/ws/pong/?mode=local&player_needed=1&host=True&room_id=1")
        communicator.scope['user'] = user

        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "game_pad")

        await communicator.send_json_to({})
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "game_error")
        self.assertIn("error", response["content"])

        await communicator.send_json_to({"type": "invalid_type"})
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "game_error")
        self.assertIn("error", response["content"])

        await communicator.send_json_to({"type": "invalid_type", "content": {}})
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "game_error")
        self.assertIn("error", response["content"])

        await communicator.disconnect()

    async def test_websocket_receive_game_ready(self):
        """
        Test if the consumer can send and receive messages, such as 'game_ready'.
        """
        user = await sync_to_async(get_user_model().objects.create_user)(username='testuser', password='password123')
        communicator = WebsocketCommunicator(Game.as_asgi(), "/ws/pong/?mode=local&player_needed=1&host=True&room_id=1")
        communicator.scope['user'] = user

        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "game_pad")

        await communicator.send_json_to({"type": "game_ready", "content": {}})
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "game_start")

        await communicator.disconnect()
