"""
ASGI config for doodhwaley project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

# doodhwaley/asgi.py
import os

import django 
django.setup
from django.core.asgi import get_asgi_application



django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter


import milkapp.views.api.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "doodhwaley.settings")


application = ProtocolTypeRouter({
  "http": django_asgi_app,
  "websocket": AuthMiddlewareStack(
        URLRouter(
            milkapp.views.api.routing.websocket_urlpatterns
        )
    ),
})
