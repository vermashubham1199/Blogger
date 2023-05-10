from django.urls import path, re_path
from .consumer import FollowNotificationConsumer


websocket_urlpatterns = [
    path('ws/notification/', FollowNotificationConsumer.as_asgi())
]