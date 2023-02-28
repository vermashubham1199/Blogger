from django.urls import path, re_path
from .consumer import ChatConsumer


websocket_urlpatterns = [
    path('ws/<str:g_name>/', ChatConsumer.as_asgi())
]