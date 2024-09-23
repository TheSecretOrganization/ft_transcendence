import asyncio
import json
import random
from uu import Error
import uuid
import redis.asyncio as redis
from typing import List
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.initialize_game()
        if self.host:
            await self.set_to_redis(self.group_name, 1)
        elif not await self.get_from_redis(
            self.group_name
        ) or await self.get_from_redis(self.room_id):
            await self.close()
            return
        self.valid_consumer = True
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send_to_group("game_join", {"user": self.scope["user"].id})
        await self.send_to_client(
            "game_pad",
            {"game_pad": self.pad_n},
        )

    def initialize_game(self):
        query_params = parse_qs(self.scope["query_string"].decode())
        room_id = query_params.get("room_id", [None])[0]
        player_needed = query_params.get("player_needed", ["1"])[0]
        self.mode = query_params.get("mode", ["local"])[0]
        self.host = room_id == None
        self.room_id = room_id if room_id else str(uuid.uuid4())
        self.group_name = f"pong_{self.room_id}"
        self.pad_n = "pad_1" if self.host else "pad_2"
        self.valid_consumer = False
        if self.host:
            self.info = self.Info(
                creator=self.scope["user"].id,
                room_id=self.room_id,
                player_needed=int(player_needed),
            )
            self.ball = self.Ball()
            self.pad_1 = self.Pad(True)
            self.pad_2 = self.Pad(False)

    async def disconnect(self, close_code):
        self.offline = True
        if not self.valid_consumer:
            return
        if self.host:
            if hasattr(self, "game_task"):
                self.game_task.cancel()
            await self.delete_redis_key(self.group_name)
            await self.delete_redis_key(self.room_id)
            if self.mode == "online" and not hasattr(self, "winner"):
                self.info.score[1] = self.info.score[0] + 1
                await self.save_pong_to_db(self.info.players[1])
            elif self.mode == "online":
                await self.save_pong_to_db(self.winner)
        await self.send_to_group("game_stop", {"user": self.scope["user"].id})
        await self.channel_layer.group_discard(
            self.group_name, self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            msg_type = data["type"]
            if not msg_type:
                raise ValueError("Missing 'type' in received data")
            if msg_type == "game_stop":
                await self.close()
            elif msg_type in ["game_ready", "game_move"]:
                await self.send_to_group(args=data)
        except Exception as e:
            print(f"Error in receive: {e}")
            await self.send_error("Invalid message format")

    async def game_join(self, event):
        if self.host:
            self.info.players.append(event["content"]["user"])
            if len(self.info.players) == self.info.player_needed:
                await self.set_to_redis(self.room_id, 1)
            await self.send_to_group("game_info", self.info.__dict__)

    async def game_info(self, event):
        await self.send_to_client(args=event)

    async def game_ready(self, event):
        if self.host:
            self.info.player_ready += 1
            if self.info.player_ready == self.info.player_needed:
                await self.send_to_group("game_start")

    async def game_start(self, event):
        await self.send_to_client(args=event)
        if self.host:
            self.game_task = asyncio.create_task(self.loop())

    async def game_state(self, event):
        await self.send_to_client(args=event)

    async def game_move(self, event):
        if self.host:
            try:
                await self.move_pad(
                    event["content"]["pad_n"], event["content"]["direction"]
                )
            except Exception as e:
                print(f"Error: {e}")

    async def game_stop(self, event):
        if hasattr(self, "offline"):
            return
        if self.host and self.mode == "online" and not hasattr(self, "winner"):
            if event["content"].get("user") == self.info.players[1]:
                self.winner = self.info.players[0]
                self.info.score[0] = self.info.score[1] + 1
            else:
                self.winner = self.info.players[1]
                self.info.score[1] = self.info.score[0] + 1
        await self.send_to_client(args=event)
        await self.close()

    async def loop(self):
        win = 5
        while True:
            try:
                self.ball.x += self.ball.velocity[0]
                self.ball.y += self.ball.velocity[1]
                self.handle_collisions()
                if self.info.score[0] == win or self.info.score[1] == win:
                    self.winner = (
                        self.info.players[0]
                        if self.info.score[0] > self.info.score[1]
                        else self.info.players[1]
                    )
                    await self.send_to_group(
                        "game_stop", {"winner": self.winner}
                    )
                    break
                await self.send_game_state()
                await asyncio.sleep(0.033)
            except Exception as e:
                print(f"Error: {e}")
                break

    async def move_pad(self, pad_number, direction):
        pad = self.pad_1 if pad_number == "pad_1" else self.pad_2
        down_lim = 1 - pad.height
        pad.move = pad.step if direction == "down" else -pad.step
        if direction == "up" and pad.y > 0:
            pad.y -= pad.step if pad.y >= pad.step else pad.y
        elif direction == "down" and pad.y < down_lim:
            pad.y += (
                pad.step if down_lim - pad.y >= pad.step else down_lim - pad.y
            )
        await self.send_game_state()

    def handle_collisions(self):
        move_factor = 0.05
        if (
            self.ball.y - self.ball.radius / 2 <= 0
            or self.ball.y + self.ball.radius / 2 >= 1
        ):
            self.ball.velocity[1] = -self.ball.velocity[1]
        if self.ball.x - self.ball.radius <= self.pad_1.x + self.pad_1.width:
            if self.pad_1.y <= self.ball.y <= self.pad_1.y + self.pad_1.height:
                self.ball.velocity[0] = -self.ball.velocity[0]
                self.ball.velocity[1] += self.pad_1.move * move_factor
            elif self.ball.x <= 0:
                self.score_point(1)
        if self.ball.x + self.ball.radius >= self.pad_2.x:
            if self.pad_2.y <= self.ball.y <= self.pad_2.y + self.pad_2.height:
                self.ball.velocity[0] = -self.ball.velocity[0]
                self.ball.velocity[1] += self.pad_2.move * move_factor
            elif self.ball.x >= 1:
                self.score_point(0)

    def score_point(self, winner: int):
        self.info.score[winner] += 1
        self.ball.reset()
        self.pad_1.reset()
        self.pad_2.reset()

    async def send_to_client(self, msg_type: str = "", args={}):
        new_args = {}
        if msg_type:
            new_args["type"] = msg_type
            new_args["content"] = args
        else:
            new_args = args
        try:
            await self.send(text_data=json.dumps(new_args))
        except Exception:
            await self.close()

    async def send_to_group(self, msg_type: str = "", args={}):
        new_args = {}
        if msg_type:
            new_args["type"] = msg_type
            new_args["content"] = args
        else:
            new_args = args
        await self.channel_layer.group_send(self.group_name, new_args)

    async def send_error(self, error: str):
        await self.send_to_client(
            "game_error",
            {
                "error": error,
            },
        )

    async def send_game_state(self):
        await self.send_to_group(
            "game_state",
            {
                "score": self.info.score,
                "ball": self.ball.__dict__,
                "pad_1": self.pad_1.__dict__,
                "pad_2": self.pad_2.__dict__,
            },
        )

    async def get_from_redis(self, key):
        client = redis.Redis(host="redis")
        value = await client.get(key)
        await client.aclose()
        return value

    async def set_to_redis(self, key, value):
        client = redis.Redis(host="redis")
        await client.set(key, value)
        await client.aclose()

    async def delete_redis_key(self, key):
        client = redis.Redis(host="redis")
        await client.delete(key)
        await client.aclose()

    async def save_pong_to_db(self, winner):
        from .models import Pong
        from ft_auth.models import User

        try:
            user1 = await sync_to_async(User.objects.get)(
                id=self.info.players[0]
            )
            user2 = await sync_to_async(User.objects.get)(
                id=self.info.players[1]
            )
            score1 = self.info.score[0]
            score2 = self.info.score[1]
            if winner == user1 and score1 < score2:
                score2 = 0
            elif winner == user2 and score1 > score2:
                score1 = 0
            await sync_to_async(Pong.objects.create)(
                user1=user1, user2=user2, score1=score1, score2=score2
            )
        except Error as e:
            print(f"Error when saving game {self.room_id} to db: {e}")

    class Info:
        def __init__(
            self,
            creator: str,
            room_id: str,
            player_needed: int,
        ):
            self.creator = creator
            self.room_id = room_id
            self.players = []
            self.player_needed = player_needed
            self.player_ready = 0
            self.score = [0, 0]

    class Ball:
        def __init__(self, radius=0.015, color="white"):
            self.reset(radius=radius, color=color)

        def reset(self, radius=0.015, color="white"):
            self.x = 0.5
            self.y = 0.5
            self.radius = radius
            self.velocity = self.randomize_velocity()
            self.color = color

        def randomize_velocity(self) -> List[float]:
            velocity = [0.01, 0.01]
            if random.randint(0, 1):
                velocity[0] *= -1
            if random.randint(0, 1):
                velocity[1] *= -1
            return velocity

    class Pad:
        def __init__(self, left, width=0.02, height=0.2, color="white"):
            self.left = left
            self.reset(width=width, height=height, color=color)

        def reset(self, width=0.02, height=0.2, color="white"):
            self.width = width
            self.height = height
            self.color = color
            self.x = 0 if self.left else 1 - self.width
            self.y = 0.4
            self.step = 0.05
            self.move = 0
