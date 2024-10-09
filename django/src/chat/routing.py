from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/General/$', ChatConsumer.as_asgi()),
    re_path(r'ws/chat/private/(?P<username>\w+)/$', ChatConsumer.as_asgi()),
]