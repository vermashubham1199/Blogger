"""
ASGI config for blogger project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing
import notification.routing
import user_profile.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blogger.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket" : AuthMiddlewareStack(
        URLRouter([
        *chat.routing.websocket_urlpatterns,
        *notification.routing.websocket_urlpatterns,
        *user_profile.routing.websocket_urlpatterns,
        ])
    )
})
