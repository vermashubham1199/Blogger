from user_profile.models import Follow
from django.dispatch import receiver
from django.db.models.signals import post_save
from blog.tests import pint
from .models import NotificationModel
from .tasks import notification_task, notification_blog_task
from channels.layers import  get_channel_layer
from blog.models import Blog

@receiver(post_save, sender=Follow)
def follow_notification(sender, instance, created, **kwargs):
    pint("post save Follow working")
    pint(instance.follower)
    pint(type(instance.owner))
    notification = NotificationModel(
        receiver = instance.owner, 
        message = f"{instance.follower} followed you!",
        sender = instance.follower,
        table_name = "Follow",
        table_row_id = str(instance.id),
    )
    notification.save()


@receiver(post_save, sender=NotificationModel)
def follow_notification_broadcasting(sender, instance, created, **kwargs):
    if instance.table_name == "Follow":
        pint("post save NotificationModel working")
        pint("notification signal")
        pint(instance.receiver.channel_name.all().first().channel_name)
        notification_task.delay(pk=instance.id)
    elif instance.table_name == "Blog":
        notification_blog_task.delay(pk=instance.id)




@receiver(post_save, sender=Blog)
def blog_notification_broadcasting(sender, instance, created, **kwargs):
    if created == True:
        pint("post save Blog working")
        pint("notification signal")
        pint(instance)
        followers = Follow.objects.filter(owner=instance.owner)
        for follower in followers:
            notification = NotificationModel(
                message = f"{instance.owner} created a new blog {instance.name}",
                sender = instance.owner,
                table_name = "Blog",
                table_row_id = str(instance.id),
                receiver = follower.follower
            )
            notification.save()