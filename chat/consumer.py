from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
import asyncio
from asgiref.sync import sync_to_async
from blog.tests import pint
from .models import Group, ChatModel
import json



class ChatConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        pint("websocket conected", event)
        self.group_name = self.scope['url_route']['kwargs']['g_name']
        pint(self.group_name)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send({
            "type":"websocket.accept"
        })
        pint("websocket connction accepted", event)
    
    async def websocket_receive(self, event):
        await self.save_message(event["text"])
        await self.channel_layer.group_send(self.group_name, {
            "type":"chat.msg",
            "message":event["text"]
         })
        pint("websocket msg received", event)
         


    async def chat_msg(self, event):
        pint(event)
        await self.send({
            "type":"websocket.send",
            "text":event["message"]
         })


    async def websocket_disconnect(self, event):
         pint("websocket disconected", event)
         raise StopConsumer
    
    @sync_to_async
    def save_message(self, msg):
        pint(msg)
        message = json.loads(msg)
        group = Group.objects.get(group_name=self.group_name)
        chat = ChatModel(message=message["msg"], group=group, user=self.scope["user"])
        chat.save()
    

