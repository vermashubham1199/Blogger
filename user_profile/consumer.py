from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
import asyncio
from asgiref.sync import sync_to_async
from blog.tests import pint
import json
from user_profile.models import Follow
from notification.models import ChannelName, NotificationModel
from django.shortcuts import get_object_or_404
from blog.models import Blog, Comment




class DashboardConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        self.user = self.scope["user"]
        pint(self.user)
        if self.user.is_authenticated:
            await self.create_channel_name()
            await self.send({
                "type":"websocket.accept"
            })
            pint("web_socket is working")
            pint(self.channel_name, "dashboard channel name")
    
    async def dashboard_send(self, event):
        await self.send({
            "type":"websocket.send",
            "text":event["message"]
         })

    async def websocket_disconnect(self, event):
         if self.user.is_authenticated:
            pint("dashboard websocket disconected", event)
            pint("websocket disconected---------------", event)
            await self.delete_channel_name()
         raise StopConsumer

    

    @sync_to_async
    def create_channel_name(self):
        channel_name = ChannelName(channel_name=self.channel_name, owner=self.user, consumer_name="DashboardConsumer")
        channel_name.save()
        self.channel_id = channel_name.id
        pint("except in dashboard create channle name", channel_name)

    @sync_to_async
    def delete_channel_name(self):
        channel_name = get_object_or_404(ChannelName, pk=self.channel_id)# will through error for the first time if you mannually delete all channel_name instances 
        channel_name.delete()
        pint("deleted channel name", channel_name)