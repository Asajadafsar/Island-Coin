import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Island.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # WebSocket URLs
    # "websocket": AuthMiddlewareStack(
    #     URLRouter(
    #         # Your WebSocket URL patterns
    #     )
    # ),
})
