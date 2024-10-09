from django.urls import re_path
from . import pong

websocket_urlpatterns = [
    re_path(r'ws/pong/?$', pong.Game.as_asgi()),
    re_path(r'ws/pong_tournament/?$', pong.Tournament.as_asgi()),
]
