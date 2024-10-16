import json
import random
from uuid import uuid4
import redis.asyncio as redis
import logging
from typing import List, Tuple
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.apps import apps
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class Tournament(AsyncWebsocketConsumer):
    async def connect(self):
        query_params = parse_qs(self.scope["query_string"].decode())
        self.redis = redis.Redis(host="redis")

        try:
            self.user = self.scope.get("user")

            if type(self.user) != get_user_model and self.user.is_anonymous:
                raise ValueError("Invalid user")

            logger.info(f"User {self.user.id} is attempting to connect.")
            self.name = query_params.get("name", [None])[0]

            if self.name == None:
                raise ValueError("Missing name")

            lock = await self.redis.get(f"pong_{self.name}_lock")
            players = await self.get_decoded_list(
                f"pong_{self.name}_usernames"
            )

            if lock != None and self.user.username not in players:
                raise ConnectionRefusedError("Tournament is locked")

        except Exception as e:
            logger.warning(f"Connection refused: {str(e)}")
            await self.close()
            return

        await self.accept()
        await self.channel_layer.group_add(self.name, self.channel_name)
        creator_encoded = await self.redis.get(f"pong_{self.name}_creator")

        if creator_encoded == None:
            await self.redis.set(
                f"pong_{self.name}_creator", self.user.username
            )
            creator_encoded = await self.redis.get(f"pong_{self.name}_creator")

        creator = creator_encoded.decode("utf-8")

        if creator == self.user.username:
            if lock == None:
                await self.send(text_data=json.dumps({"type": "unlock_lock"}))
            else:
                await self.archive()

        await self.send_history()
        await self.check_current_games_state()

        if self.user.username not in players:
            await self.redis.rpush(
                f"pong_{self.name}_usernames", self.user.username
            )
            await self.redis.rpush(
                f"pong_{self.name}_players", self.user.username
            )

        await self.channel_layer.group_send(self.name, {"type": "join"})

    async def disconnect(self, close_code):
        creator_encoded = await self.redis.get(f"pong_{self.name}_creator")
        creator = creator_encoded.decode("utf-8")

        if hasattr(self, "over") and creator == self.user.username:
            await self.redis.delete(f"pong_{self.name}_lock")
            await self.redis.delete(f"pong_{self.name}_ready")
            await self.redis.delete(f"pong_{self.name}_creator")
            await self.redis.delete(f"pong_{self.name}_players")
            await self.redis.delete(f"pong_{self.name}_usernames")
            await self.redis.delete(f"pong_{self.name}_current_games")
            await self.redis.delete(f"pong_{self.name}_history")

        await self.channel_layer.group_discard(self.name, self.channel_name)
        await self.redis.close()
        logger.info(f"User {self.scope['user'].id} has disconnected.")

    async def receive(self, text_data):
        data = json.loads(text_data)

        try:
            msg_type = data.get("type")

            if not msg_type:
                raise AttributeError("Missing 'type'")

            logger.debug(
                f"Received '{msg_type}' message from user {self.scope['user'].id}."
            )

            match msg_type:
                case "lock":
                    await self.lock()
                case "ready":
                    await self.ready()
                case "mix":
                    await self.mix()
                case _:
                    raise ValueError("Unknown 'type' in data")
        except Exception as e:
            logger.warning(
                f"Invalid message received from user {self.scope['user'].id}: {str(e)}"
            )
            await self.send(
                text_data=json.dumps({"type": "error", "content": str(e)})
            )

    async def join(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "join",
                    "players": await self.get_decoded_list(
                        f"pong_{self.name}_usernames"
                    ),
                }
            )
        )

    async def lock(self):
        await self.redis.set(f"pong_{self.name}_lock", 1)
        await self.channel_layer.group_send(
            self.name, {"type": "unlock_ready"}
        )

    async def unlock_ready(self, event):
        await self.send(text_data=json.dumps({"type": "unlock_ready"}))

    async def ready(self):
        players = await self.get_decoded_list(f"pong_{self.name}_players")
        await self.redis.incr(f"pong_{self.name}_ready")
        ready_encoded = await self.redis.get(f"pong_{self.name}_ready")
        ready = int(ready_encoded.decode("utf-8"))

        if ready >= len(players):
            await self.channel_layer.group_send(
                self.name, {"type": "unlock_mix"}
            )
            self.redis.set(f"pong_{self.name}_ready", 0)

    async def unlock_mix(self, event):
        if await self.redis.get(
            f"pong_{self.name}_creator"
        ) == self.user.username.encode("utf-8"):
            await self.send(text_data=json.dumps({"type": "unlock_mix"}))

    async def mix(self):
        players = await self.get_decoded_list(f"pong_{self.name}_players")
        random.shuffle(players)
        player_pairs = []
        uuid_list = []
        last_player = None

        if len(players) % 2 != 0:
            last_player = players.pop()

        for i in range(0, len(players), 2):
            player_pairs.append((players[i], players[i + 1]))
            id = str(uuid4())
            uuid_list.append(id)
            await self.redis.rpush(f"pong_{self.name}_current_games", id)

        if last_player:
            player_pairs.append((last_player, "-"))
            players.append(last_player)

        await self.channel_layer.group_send(
            self.name,
            {
                "type": "get_next_round_id",
                "player_pairs": player_pairs,
                "uuid_list": uuid_list,
            },
        )

    async def get_next_round_id(self, event):
        player_pairs: List[Tuple] = event["player_pairs"]
        uuid_list: List = event["uuid_list"]
        await self.send(
            text_data=json.dumps({"type": "mix", "player_pairs": player_pairs})
        )

        for i, (player1, player2) in enumerate(player_pairs):
            if self.user.username not in (player1, player2):
                continue

            message = (
                {"type": "bye"}
                if player2 == "-"
                else {"type": "next_round_id", "id": uuid_list[i]}
            )
            await self.send(text_data=json.dumps(message))
            break

    async def archive(self):
        pong = apps.get_model("games", "Pong")
        current_games = await self.get_decoded_list(
            f"pong_{self.name}_current_games"
        )

        for uuid in current_games:
            try:
                game = await sync_to_async(pong.objects.get)(uuid=uuid)
                await self.redis.lrem(
                    f"pong_{self.name}_current_games", 1, uuid
                )
                await self.redis.rpush(
                    f"pong_{self.name}_history",
                    json.dumps(
                        {
                            "user1": await sync_to_async(
                                lambda: game.user1.username
                            )(),
                            "user2": await sync_to_async(
                                lambda: game.user2.username
                            )(),
                            "score1": game.score1,
                            "score2": game.score2,
                        }
                    ),
                )
            except pong.DoesNotExist:
                continue

    async def send_history(self):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "history",
                    "history": await self.get_decoded_list(
                        f"pong_{self.name}_history"
                    ),
                }
            )
        )

    async def check_current_games_state(self):
        current_games = await self.get_decoded_list(
            f"pong_{self.name}_current_games"
        )

        if len(current_games) <= 0:
            await self.channel_layer.group_send(
                self.name, {"type": "unlock_ready"}
            )

    async def get_decoded_list(self, name):
        l = await self.redis.lrange(name, 0, -1)
        decoded_list = [el.decode("utf-8") for el in l]
        return decoded_list
