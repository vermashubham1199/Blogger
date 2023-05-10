from .models import Follow
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from blog.tests import pint
from .tasks import  dashboard_task
from channels.layers import  get_channel_layer
from blog.models import Blog, Comment, Like, Bookmark, BlogHistory 
import json




@receiver(post_save, sender=Comment)
def comment_dashboard_signal(sender, instance, created, **kwargs):
    blog_id = instance.blog.id
    channel_name = (list(instance.blog.owner.channel_name.filter(consumer_name="DashboardConsumer")))
    channel_list = [c.channel_name for c in channel_name]
    created_date = str(instance.created_at.date())
    pint("post save Commnet working in user_profile.signals")
    pint(instance)
    pint(type(instance.owner))
    output = {"table_name":"Commnet", "channel_list":channel_list, "created_date":created_date, "blog_id":blog_id}
    dashboard_task.delay(**output)


@receiver(post_save, sender=Like)
def like_dashboard_signal(sender, instance, created, **kwargs):
    blog_id = instance.blog.id
    channel_name = (list(instance.blog.owner.channel_name.filter(consumer_name="DashboardConsumer")))
    channel_list = [c.channel_name for c in channel_name]
    if created:
        if instance.like:
            created_date = str(instance.created_at.date())
            pint("post save Commnet working in user_profile.signals")
            pint(instance)
            pint(type(instance.owner))
            output = {"table_name":"Like", "channel_list":channel_list, "created_date":created_date, "blog_id":blog_id, "like_value":True}
            dashboard_task.delay(**output)
    else:
        if instance.like:
            created_date = str(instance.created_at.date())
            pint("post save Commnet working in user_profile.signals")
            pint(instance)
            pint(type(instance.owner))
            output = {"table_name":"Like", "channel_list":channel_list, "created_date":created_date, "blog_id":blog_id, "like_value":True}
            dashboard_task.delay(**output)
        else:
            created_date = str(instance.created_at.date())
            pint("post save inner else Commnet working in user_profile.signals")
            pint(instance)
            pint(type(instance.owner))
            output = {"table_name":"Like", "channel_list":channel_list, "created_date":created_date, "blog_id":blog_id, "like_value":False}
            dashboard_task.delay(**output)



@receiver(post_save, sender=Bookmark)
def bookmark_dashboard_signal(sender, instance, created, **kwargs):
    blog_id = instance.blog.id
    channel_name = (list(instance.blog.owner.channel_name.filter(consumer_name="DashboardConsumer")))
    channel_list = [c.channel_name for c in channel_name]
    created_date = str(instance.created_at.date())
    pint("post save Commnet working in user_profile.signals")
    pint(instance)
    pint(type(instance.owner))
    output = {"table_name":"Bookmark", "channel_list":channel_list, "created_date":created_date, "blog_id":blog_id}
    dashboard_task.delay(**output)


@receiver(post_save, sender=BlogHistory)
def blog_history_dashboard_signal(sender, instance, created, **kwargs):
    blog_id = instance.blog.id
    channel_name = (list(instance.blog.owner.channel_name.filter(consumer_name="DashboardConsumer")))
    pint(type(channel_name), "channle name type")
    pint(channel_name)
    channel_list = [c.channel_name for c in channel_name]
    pint(channel_list)
    created_date = str(instance.created_at.date())
    pint("post save Commnet working in user_profile.signals")
    pint(instance)
    pint(type(instance.owner))
    output = {"table_name":"BlogHistory", "channel_list":channel_list, "created_date":created_date, "blog_id":blog_id}
    dashboard_task.delay(**output)
    


@receiver(post_delete, sender=Like)
def like_delete_dashboard_signal(sender, instance, **kwargs):
    blog_id = instance.blog.id
    channel_name = (list(instance.blog.owner.channel_name.filter(consumer_name="DashboardConsumer")))
    channel_list = [c.channel_name for c in channel_name]
    if instance.like:
        created_date = str(instance.created_at.date())
        pint("post save Commnet working in user_profile.signals")
        pint(instance)
        pint(type(instance.owner))
        output = {"table_name":"Like", "channel_list":channel_list, "created_date":created_date, "blog_id":blog_id, "like_value":True, "dele":True}
        dashboard_task.delay(**output)


@receiver(post_delete, sender=Comment)
def comment_dashboard_signal(sender, instance, **kwargs):
    blog_id = instance.blog.id
    channel_name = (list(instance.blog.owner.channel_name.filter(consumer_name="DashboardConsumer")))
    channel_list = [c.channel_name for c in channel_name]
    created_date = str(instance.created_at.date())
    pint("post save Commnet working in user_profile.signals")
    pint(instance)
    pint(type(instance.owner))
    output = {"table_name":"Commnet", "channel_list":channel_list, "created_date":created_date, "blog_id":blog_id, "dele":True}
    dashboard_task.delay(**output)


@receiver(post_delete, sender=Bookmark)
def bookmark_dashboard_signal(sender, instance, **kwargs):
    blog_id = instance.blog.id
    channel_name = (list(instance.blog.owner.channel_name.filter(consumer_name="DashboardConsumer")))
    channel_list = [c.channel_name for c in channel_name]
    created_date = str(instance.created_at.date())
    pint("post save Commnet working in user_profile.signals")
    pint(instance)
    pint(type(instance.owner))
    output = {"table_name":"Bookmark", "channel_list":channel_list, "created_date":created_date, "blog_id":blog_id, "dele":True}
    dashboard_task.delay(**output)