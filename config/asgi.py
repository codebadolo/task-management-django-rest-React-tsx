"""
ASGI config for project_management project.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    # WebSocket pour les notifications en temps réel
    'websocket': AuthMiddlewareStack(
        URLRouter([
            # Ajouter vos routes WebSocket ici
        ])
    ),
})
