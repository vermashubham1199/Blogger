from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    group_name = models.CharField(max_length=550)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1_group')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2_group')

    def __str__(self) -> str:
      return str(self.group_name)
    
    class Meta:
        unique_together = ('user1','user2')

class ChatModel(models.Model):
    message = models.TextField()
    timestamp = models.TimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_chat')
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='group_chat')

    def __str__(self) -> str:
        return str(self.user.first_name)
    

