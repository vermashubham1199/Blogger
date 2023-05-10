from django.urls import path, re_path
from .consumer import DashboardConsumer


websocket_urlpatterns = [
    path('ws/dashboard/', DashboardConsumer.as_asgi())
]