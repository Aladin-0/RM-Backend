# restromanager/asgi.py

import os
from django.core.asgi import get_asgi_application

# IMPORTANT: Django's get_asgi_application() needs to be called before we import
# anything else from Django, so we do it at the top.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restromanager.settings')
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import menu.routing

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,

    # WebSocket chat handler
    "websocket": AuthMiddlewareStack(
        URLRouter(
            menu.routing.websocket_urlpatterns
        )
    ),
})