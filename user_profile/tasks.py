from celery import shared_task
from channels.layers import  get_channel_layer
from asgiref.sync import sync_to_async
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
from blog.models import Blog, Comment


@shared_task(bind=True)
def dashboard_task(self, channel_list, **kwargs):
    pint(channel_list, "channel name in user_profile.tasks.py")
    pint(kwargs, "kwargs in user_profile.tasks.py")
    channel_layer = get_channel_layer()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    pint(channel_layer, "channel_layer in user_profile")
    for  channel_name in channel_list:
        loop.run_until_complete(
            channel_layer.send(
            channel_name,
            {
            "type":"dashboard.send",
            "message":json.dumps(kwargs) 
            }
            )
        )

