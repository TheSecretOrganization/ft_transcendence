from django.urls import re_path
from . import pong

websocket_urlpatterns = [
    re_path(r'ws/pong/?$', pong.Consumer.as_asgi()),
]
