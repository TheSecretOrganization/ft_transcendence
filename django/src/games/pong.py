import asyncio
import json
import random
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
            await self.redis.set(self.group_name, 1)
        elif not await self.redis.get(self.group_name) or await self.redis.get(self.room_id):
            await self.close()
            return
        self.valid_consumer = True
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send_message("group", "game_join", {"user": self.scope["user"].id})
        await self.send_message("client", "game_pad", {"game_pad": self.pad_n})

    def initialize_game(self):
        self.redis = redis.Redis(host="redis")
        query_params = parse_qs(self.scope["query_string"].decode())
        self.mode = query_params.get("mode", ["local"])[0]
        room_id = query_params.get("room_id", [None])[0]
        self.host = room_id is None
        self.room_id = room_id or str(uuid.uuid4())
        self.group_name = f"pong_{self.room_id}"
        self.pad_n = "pad_1" if self.host else "pad_2"
        self.valid_consumer = False
        if self.host:
            self.info = self.Info(
                creator=self.scope["user"].id,
                room_id=self.room_id,
                player_needed=int(query_params.get("player_needed", ["1"])[0]),
            )
            self.ball = self.Ball()
            self.pad_1 = self.Pad(True)
            self.pad_2 = self.Pad(False)

    async def disconnect(self, close_code):
        self.offline = True
        if self.host:
            if hasattr(self, "game_task"):
                self.game_task.cancel()
            await self.redis.delete(self.group_name)
            await self.redis.delete(self.room_id)
            if self.mode == "online":
                if not hasattr(self, "winner"):
                    self.punish_coward(self.info.creator)
                await self.save_pong_to_db(self.winner)
        if self.valid_consumer:
            await self.send_message("group", "game_stop", {"user": self.scope["user"].id})
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.redis.aclose()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            msg_type = data["type"]
            if not msg_type:
                raise ValueError("Missing 'type' in received data")
            if msg_type == "game_stop":
                await self.close()
            elif msg_type in ["game_ready", "game_move"]:
                await self.send_message("group", args=data)
        except ValueError as e:
            print(f"Value error: {e}")
            await self.send_error(str(e))
        except Exception as e:
            print(f"Unexpected error in receive: {e}")
            await self.send_error("An unexpected error occurred")

    async def game_join(self, event):
        if self.host:
            self.info.players.append(event["content"]["user"])
            if len(self.info.players) == self.info.player_needed:
                await self.redis.set(self.room_id, 1)
            await self.send_message("group", "game_info", self.info.__dict__)

    async def game_info(self, event):
        await self.send_message("client", args=event)

    async def game_ready(self, event):
        if self.host:
            self.info.player_ready += 1
            if self.info.player_ready == self.info.player_needed:
                await self.send_message("group", "game_start")

    async def game_start(self, event):
        await self.send_message("client", args=event)
        if self.host:
            self.game_task = asyncio.create_task(self.loop())

    async def game_state(self, event):
        await self.send_message("client", args=event)

    async def game_move(self, event):
        if self.host:
            await self.move_pad(event["content"]["pad_n"], event["content"]["direction"])

    async def game_stop(self, event):
        if hasattr(self, "offline"):
            return
        if self.host:
            self.winner = event["content"].get("winner")
            if not self.winner:
                self.punish_coward(event["content"].get("user"))
        await self.send_message("client", args=event)
        await self.close()

    def punish_coward(self, coward):
        if not coward:
            return
        if coward is self.info.players[0]:
            self.info.score[1] = self.info.score[0] + 1
        else:
            self.info.score[0] = self.info.score[1] + 1
        self.winner = self.get_winner()

    async def loop(self):
        win = 5
        fps = 0.033
        while True:
            try:
                self.ball.move()
                self.handle_collisions()
                if self.info.score[0] == win or self.info.score[1] == win:
                    await self.send_message("group", "game_stop", {"winner": self.get_winner()})
                    break
                await self.send_game_state()
                await asyncio.sleep(fps)
            except Exception as e:
                print(f"Unexpected error in the loop from game {self.room_id}: {e}")
                break

    def get_winner(self):
        if self.mode == "online":
            return self.info.players[0] if self.info.score[0] > self.info.score[1] else self.info.players[1]
        else:
            return "Pad 1" if self.info.score[0] > self.info.score[1] else "Pad 2"

    async def move_pad(self, pad_number, direction):
        pad = self.pad_1 if pad_number == "pad_1" else self.pad_2
        step = pad.step if direction == "down" else -pad.step
        pad.y = min(max(pad.y + step, 0), 1 - pad.height)
        await self.send_game_state()

    def handle_collisions(self):
        if self.ball.y - self.ball.radius / 2 <= 0 or self.ball.y + self.ball.radius / 2 >= 1:
            self.ball.revert_velocity(1)
        elif self.check_pad_collision():
            self.ball.revert_velocity(0)
            if self.ball.x < 0.5:
                self.ball.x = self.pad_1.width + self.ball.radius / 2
            else:
                self.ball.x = 1 - self.pad_2.width - self.ball.radius / 2
        elif self.ball.x + self.ball.radius / 2 <= self.pad_1.width:
            self.score_point(1)
        elif self.ball.x - self.ball.radius / 2 >= 1 - self.pad_2.width:
            self.score_point(0)

    def check_pad_collision(self):
        if self.ball.x - self.ball.radius <= self.pad_1.width:
            if self.pad_1.y <= self.ball.y <= self.pad_1.y + self.pad_1.height:
                return True
        if self.ball.x + self.ball.radius >= 1 - self.pad_2.width:
            if self.pad_2.y <= self.ball.y <= self.pad_2.y + self.pad_2.height:
                return True
        return False

    def score_point(self, winner: int):
        self.info.score[winner] += 1
        self.ball.reset()
        self.pad_1.reset()
        self.pad_2.reset()

    async def send_message(self, destination="client", msg_type="", args={}):
        message = {"type": msg_type, "content": args} if msg_type else args
        if destination == "group":
            await self.channel_layer.group_send(self.group_name, message)
        elif destination == "client":
            await self.send(text_data=json.dumps(message))

    async def send_error(self, error: str):
        await self.send_message("client", "game_error", {"error": error})

    async def send_game_state(self):
        await self.send_message(
            "group",
            "game_state",
            {
                "score": self.info.score,
                "ball": self.ball.__dict__,
                "pad_1": self.pad_1.__dict__,
                "pad_2": self.pad_2.__dict__,
            },
        )

    async def save_pong_to_db(self, winner):
        from .models import Pong
        from ft_auth.models import User

        try:
            await sync_to_async(Pong.objects.create)(
                user1=await sync_to_async(User.objects.get)(id=self.info.players[0]),
                user2=await sync_to_async(User.objects.get)(id=self.info.players[1]),
                score1=self.info.score[0],
                score2=self.info.score[1]
            )
        except Exception as e:
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
            self.y = random.uniform(0.2, 0.8)
            self.radius = radius
            self.velocity = self.randomize_velocity()
            self.color = color
            self.step = 0.05

        def randomize_velocity(self) -> List[float]:
            velocity = [0.01, 0.01]
            if random.randint(0, 1):
                velocity[0] *= -1
            if random.randint(0, 1):
                velocity[1] *= -1
            return velocity

        def revert_velocity(self, index):
            self.velocity[index] = -self.velocity[index]

        def move(self):
            self.x += self.velocity[0]
            self.y += self.velocity[1]

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
