from celery import shared_task
from channels.layers import  get_channel_layer
from asgiref.sync import sync_to_async
from .models import NotificationModel
from celery import Celery, states
from celery.exceptions import Ignore
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
import asyncio
import json
import traceback
from blog.tests import pint
from django.shortcuts import get_object_or_404
import datetime
import time
from blog.models import Blog


@shared_task(bind=True)
def notification_task(self, pk, channel_list):
    channel_layer = get_channel_layer()
    pint(channel_layer, "channel_layer in notification")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for  channel_name in channel_list:
        pint(channel_name)
        loop.run_until_complete(
            channel_layer.send(
            channel_name,
            {
            "type":"notification.send",
            "notification_message":json.dumps({
            "notification_id":pk
            }) 
            }
            )
        )

@shared_task(bind=True)
def notification_blog_task(self, pk, group_name):
    pint(group_name, "group_name in notification tasks.py line 41")
    channel_layer = get_channel_layer()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(
        channel_layer.group_send(
        group_name,
        {
        "type":"notification.groupsend",
        "notification_message":json.dumps({
        "notification_id":pk,
        "group_name":group_name
        }) 
        }
        )
    )


# @shared_task(bind=True)
# def notification_blog_task(self,pk):
#     pint("celery blog notification task working")
#     pint(pk)
#     notification_row = get_object_or_404(NotificationModel, pk=pk)
#     group_name = notification_row.sender.username
#     pint(group_name)
#     pint(pk, group_name)
#     # channel_layer = get_channel_layer()
#     # loop = asyncio.new_event_loop()
#     # asyncio.set_event_loop(loop)
#     # loop.run_until_complete(
#     #     channel_layer.group_send(
#     #     group_name,
#     #     {
#     #     "type":"notification.groupsend",
#     #     "notification_message":json.dumps({
#     #     "blog_id":pk
#     #     }) 
#     #     }
#     #     )
#     # )