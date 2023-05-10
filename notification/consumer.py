from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
import asyncio
from asgiref.sync import sync_to_async
from blog.tests import pint
import json
from user_profile.models import Follow
from .models import ChannelName, NotificationModel
from django.shortcuts import get_object_or_404
from blog.models import Blog


class FollowNotificationConsumer(AsyncConsumer):

    async def websocket_connect(self,event):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            await self.create_channel_name()
            await self.channel_layer.group_add(self.user.username, self.channel_name)
            for i in await self.get_followed_users_list():
                await self.channel_layer.group_add(i, self.channel_name)
                pint("group name", i)
            await self.get_followed_users_list()
            await self.send({
                "type":"websocket.accept"
            })
        pint("web_socket is working")
        pint(self.channel_name, "notification channel name")

    @sync_to_async
    def get_followed_users_list(self):
        user = self.scope["user"]
        followed  = Follow.objects.filter(follower=user)
        return [i.owner.username for i in followed]


    async def websocket_disconnect(self, event):
         if self.user.is_authenticated:
            pint("websocket disconected---------------", event)
            await self.delete_channel_name()
         raise StopConsumer
    
    async def notification_send(self, event):
        pint(event["notification_message"], "message received from celery")
        notification_id = json.loads(event["notification_message"])["notification_id"]
        notification_object = await sync_to_async(get_object_or_404)(NotificationModel, pk=notification_id)
        await self.send({
            "type":"websocket.send",
            "text":json.dumps({
            "notification_msg":notification_object.message,
            "notification_msg_time":str(notification_object.date)
            })
         })

    async def notification_groupsend(self, event):
        pint(event["notification_message"], "message received from celery in notification send blog")
        notification_id = json.loads(event["notification_message"])["notification_id"]
        group_name = json.loads(event["notification_message"])["group_name"]
        # blog_object = await sync_to_async(get_object_or_404)(Blog, pk=blog_id)
        # blog_owner = await self.get_blog_owner(blog_id)
        user = self.scope["user"]
        if user != group_name:
            pint(self.scope["user"], "users in notification_groupsend")
            await self.send({
                "type":"websocket.send",
                "text":json.dumps({
                "notification_msg":f"{notification_id} just posted a new blog ",
                "notification_id":notification_id
                })
            })
    
    


    @sync_to_async
    def create_channel_name(self):
        channel_name = ChannelName(channel_name=self.channel_name, owner=self.user, consumer_name="FollowNotificationConsumer")
        channel_name.save()
        self.channel_id = channel_name.id
        pint("except in dashboard create channle name", channel_name)

    @sync_to_async
    def delete_channel_name(self):
        channel_name = get_object_or_404(ChannelName, pk=self.channel_id)
        channel_name.delete()
        pint("deleted channel name", channel_name)

    
    @sync_to_async
    def get_blog_owner(self, pk):
        blog = get_object_or_404(Blog, pk=pk)
        return blog.owner