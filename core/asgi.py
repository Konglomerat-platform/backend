"""ASGI config for Konglomerat."""
import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

django_asgi_application = get_asgi_application()

from apps.communications.routing import websocket_urlpatterns  # noqa: E402
from apps.communications.ws_auth import JwtAuthMiddleware  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_application,
        "websocket": JwtAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
