from enum import unique
from statistics import mode
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ProfilePic(models.Model):
    picture = models.BinaryField(null = True, blank = True, editable=True)
    content_type = models.CharField(max_length=256, null=True, blank=True, help_text='The MIMEType of the file')
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile_pic')


class Chat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_chat')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver_chat')

    class Meta:
        unique_together = ('sender', 'receiver')

class UserMessage(models.Model):
    text = models.CharField(max_length=256)
    chat =  models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='user_message')
    created_at = models.DateTimeField(auto_now_add=True)

class Follow(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_owner_follow')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_follower')

    def __str__(self) -> str:
        return self.owner.username

    class Meta:
        unique_together = ('follower', 'owner')