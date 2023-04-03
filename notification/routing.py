from django.urls import path, re_path
from .consumer import FollowNotificationConsumer


websocket_urlpatterns = [
    path('ws/notification/<int:pk>', FollowNotificationConsumer.as_asgi())
]