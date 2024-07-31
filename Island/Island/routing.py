# Island/routing.py

from django.urls import path
from Front import consumers

websocket_urlpatterns = [
    path('ws/user/<int:user_id>/', consumers.UserCoinsConsumer.as_asgi()),
]
