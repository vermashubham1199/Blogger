from django.db import models
from django.contrib.auth.models import User


class NotificationModel(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_notification_receiver",null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_notification_sender")
    message = models.TextField(max_length=256)
    date = models.DateTimeField(auto_now=True)
    seen = models.BooleanField(default=False)
    table_name =  models.CharField(max_length=256)
    table_row_id = models.CharField(max_length=256)

    def __str__(self) -> str:
        return f"{self.message}  {self.receiver}"
    
class ChannelName(models.Model):
    channel_name =  models.CharField(max_length=256)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="channel_name")


    def __str__(self) -> str:
        return f"{self.owner}  {self.channel_name}"



