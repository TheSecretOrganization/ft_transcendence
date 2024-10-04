# from django.urls import re_path
# from .cusomers import ChatConsumer

# websocket_urlpatterns = [
# 	re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
# ]

from django.urls import re_path
from .cusomers import ChatConsumer

websocket_urlpatterns = [
    # Route pour la salle générale
    re_path(r'ws/chat/General/$', ChatConsumer.as_asgi()),

    # Route pour les chats privés entre utilisateurs
    re_path(r'ws/chat/private/(?P<username>\w+)/$', ChatConsumer.as_asgi()),
]

